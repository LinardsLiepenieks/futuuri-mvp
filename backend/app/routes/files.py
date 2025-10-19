from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import logging
from app.config import STORAGE_SERVICE_URL

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/files/{report_id}/report/{filename}")
async def proxy_report_file(report_id: str, filename: str, request: Request):
    """Stream report image from storage-service to client without buffering whole file.

    This wrapper logs and converts unexpected exceptions into 502 responses so
    clients don't get 500 without diagnostics.
    """
    storage_url = (
        f"{STORAGE_SERVICE_URL.rstrip('/')}/api/files/{report_id}/report/{filename}"
    )

    try:
        # Forward Range and Authorization headers if present
        headers = {}
        if "range" in request.headers:
            headers["Range"] = request.headers["range"]
        if "authorization" in request.headers:
            headers["Authorization"] = request.headers["authorization"]

        client = httpx.AsyncClient(timeout=60.0)
        # Do a HEAD first to obtain headers and status without consuming the body.
        try:
            try:
                head_resp = await client.head(
                    storage_url, headers=headers, timeout=20.0
                )
            except httpx.HTTPError as e:
                log.exception(
                    "HTTP error while contacting upstream (HEAD) %s: %s", storage_url, e
                )
                await client.aclose()
                raise HTTPException(status_code=502, detail=str(e))

            if head_resp.status_code >= 400:
                # Some upstreams don't implement HEAD (405). In that case, fall
                # back to opening a GET stream to inspect headers and then
                # stream the body without buffering.
                if head_resp.status_code == 405:
                    # Open GET stream now and extract headers from GET response.
                    stream_cm = client.stream(
                        "GET", storage_url, headers=headers, timeout=60.0
                    )
                    try:
                        resp = await stream_cm.__aenter__()
                    except httpx.HTTPError as e:
                        log.exception(
                            "HTTP error while contacting upstream (GET) %s: %s",
                            storage_url,
                            e,
                        )
                        try:
                            await client.aclose()
                        except Exception:
                            pass
                        raise HTTPException(status_code=502, detail=str(e))

                    if resp.status_code >= 400:
                        err_bytes = await resp.aread()
                        try:
                            detail = err_bytes.decode()
                        except Exception:
                            detail = str(err_bytes)
                        # close the stream and client
                        try:
                            await stream_cm.__aexit__(None, None, None)
                        except Exception:
                            pass
                        try:
                            await client.aclose()
                        except Exception:
                            pass
                        raise HTTPException(status_code=resp.status_code, detail=detail)

                    # Build headers_out from GET response headers (do NOT forward Content-Length)
                    headers_out = {}
                    for h in (
                        "content-range",
                        "accept-ranges",
                        "content-disposition",
                        "cache-control",
                        "etag",
                    ):
                        if h in resp.headers:
                            headers_out[h] = resp.headers[h]

                    content_type = resp.headers.get(
                        "content-type", "application/octet-stream"
                    )
                    status = resp.status_code if resp.status_code else 200

                    async def stream_generator():
                        try:
                            async for chunk in resp.aiter_bytes(chunk_size=32_768):
                                if not chunk:
                                    continue
                                yield chunk
                        except Exception as e:
                            log.exception(
                                "Error while streaming from upstream %s: %s",
                                storage_url,
                                e,
                            )
                            return
                        finally:
                            try:
                                await stream_cm.__aexit__(None, None, None)
                            except Exception:
                                pass
                            try:
                                await client.aclose()
                            except Exception:
                                pass

                    return StreamingResponse(
                        stream_generator(),
                        status_code=status,
                        media_type=content_type,
                        headers=headers_out,
                    )

                detail = head_resp.text
                log.warning(
                    "Upstream HEAD returned error %s for %s: %s",
                    head_resp.status_code,
                    storage_url,
                    detail,
                )
                await client.aclose()
                raise HTTPException(status_code=head_resp.status_code, detail=detail)

            # Build headers_out from HEAD response but do NOT forward Content-Length
            headers_out = {}
            for h in (
                "content-range",
                "accept-ranges",
                "content-disposition",
                "cache-control",
                "etag",
            ):
                if h in head_resp.headers:
                    headers_out[h] = head_resp.headers[h]

            content_type = head_resp.headers.get(
                "content-type", "application/octet-stream"
            )
            status = head_resp.status_code if head_resp.status_code else 200

            async def stream_generator():
                try:
                    async with client.stream(
                        "GET", storage_url, headers=headers, timeout=60.0
                    ) as resp:
                        if resp.status_code >= 400:
                            # read small error body safely
                            err_bytes = await resp.aread()
                            try:
                                detail = err_bytes.decode()
                            except Exception:
                                detail = str(err_bytes)
                            log.warning(
                                "Upstream GET returned error %s for %s: %s",
                                resp.status_code,
                                storage_url,
                                detail,
                            )
                            return

                        async for chunk in resp.aiter_bytes(chunk_size=32_768):
                            if not chunk:
                                continue
                            yield chunk
                except Exception as e:
                    log.exception(
                        "Error while streaming from upstream %s: %s", storage_url, e
                    )
                    return
                finally:
                    # close the client once streaming finishes (or on error)
                    try:
                        await client.aclose()
                    except Exception:
                        pass

            return StreamingResponse(
                stream_generator(),
                status_code=status,
                media_type=content_type,
                headers=headers_out,
            )
        except HTTPException:
            # ensure client is closed on early HTTPException
            try:
                await client.aclose()
            except Exception:
                pass
            raise
        except Exception as e:
            try:
                await client.aclose()
            except Exception:
                pass
            log.exception("Failed to proxy report file %s -> %s", storage_url, e)
            raise HTTPException(status_code=502, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Failed to proxy report file %s -> %s", storage_url, e)
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/files/{report_id}/mask")
async def proxy_mask_file(report_id: str, request: Request):
    """Stream mask image from storage-service to client without buffering whole file.

    Add logging and robust error handling to return 502 on upstream failures.
    """
    storage_url = f"{STORAGE_SERVICE_URL.rstrip('/')}/api/files/{report_id}/mask"

    try:
        headers = {}
        if "authorization" in request.headers:
            headers["Authorization"] = request.headers["authorization"]
        # forward Range header for mask as well (support partial requests)
        if "range" in request.headers:
            headers["Range"] = request.headers["range"]

        client = httpx.AsyncClient(timeout=60.0)
        try:
            try:
                head_resp = await client.head(
                    storage_url, headers=headers, timeout=20.0
                )
            except httpx.HTTPError as e:
                log.exception(
                    "HTTP error while contacting upstream (HEAD) %s: %s", storage_url, e
                )
                await client.aclose()
                raise HTTPException(status_code=502, detail=str(e))

            if head_resp.status_code >= 400:
                # Fallback for upstreams that don't support HEAD (405): open GET and stream
                if head_resp.status_code == 405:
                    stream_cm = client.stream(
                        "GET", storage_url, headers=headers, timeout=60.0
                    )
                    try:
                        resp = await stream_cm.__aenter__()
                    except httpx.HTTPError as e:
                        log.exception(
                            "HTTP error while contacting upstream (GET) %s: %s",
                            storage_url,
                            e,
                        )
                        try:
                            await client.aclose()
                        except Exception:
                            pass
                        raise HTTPException(status_code=502, detail=str(e))

                    if resp.status_code >= 400:
                        err_bytes = await resp.aread()
                        try:
                            detail = err_bytes.decode()
                        except Exception:
                            detail = str(err_bytes)
                        try:
                            await stream_cm.__aexit__(None, None, None)
                        except Exception:
                            pass
                        try:
                            await client.aclose()
                        except Exception:
                            pass
                        raise HTTPException(status_code=resp.status_code, detail=detail)

                    headers_out = {}
                    for h in (
                        "content-range",
                        "accept-ranges",
                        "content-disposition",
                        "cache-control",
                        "etag",
                    ):
                        if h in resp.headers:
                            headers_out[h] = resp.headers[h]

                    content_type = resp.headers.get(
                        "content-type", "application/octet-stream"
                    )
                    status = resp.status_code if resp.status_code else 200

                    async def stream_generator():
                        try:
                            async for chunk in resp.aiter_bytes(chunk_size=32_768):
                                if not chunk:
                                    continue
                                yield chunk
                        except Exception as e:
                            log.exception(
                                "Error while streaming from upstream %s: %s",
                                storage_url,
                                e,
                            )
                            return
                        finally:
                            try:
                                await stream_cm.__aexit__(None, None, None)
                            except Exception:
                                pass
                            try:
                                await client.aclose()
                            except Exception:
                                pass

                    return StreamingResponse(
                        stream_generator(),
                        status_code=status,
                        media_type=content_type,
                        headers=headers_out,
                    )

                detail = head_resp.text
                await client.aclose()
                raise HTTPException(status_code=head_resp.status_code, detail=detail)

            headers_out = {}
            for h in (
                "content-range",
                "accept-ranges",
                "content-disposition",
                "cache-control",
                "etag",
            ):
                if h in head_resp.headers:
                    headers_out[h] = head_resp.headers[h]

            content_type = head_resp.headers.get(
                "content-type", "application/octet-stream"
            )
            status = head_resp.status_code if head_resp.status_code else 200

            async def stream_generator():
                try:
                    async with client.stream(
                        "GET", storage_url, headers=headers, timeout=60.0
                    ) as resp:
                        if resp.status_code >= 400:
                            err_bytes = await resp.aread()
                            try:
                                detail = err_bytes.decode()
                            except Exception:
                                detail = str(err_bytes)
                            log.warning(
                                "Upstream GET returned error %s for %s during GET: %s",
                                resp.status_code,
                                storage_url,
                                detail,
                            )
                            return

                        async for chunk in resp.aiter_bytes(chunk_size=32_768):
                            if not chunk:
                                continue
                            yield chunk
                except Exception as e:
                    log.exception(
                        "Error while streaming from upstream %s: %s", storage_url, e
                    )
                    return
                finally:
                    try:
                        await client.aclose()
                    except Exception:
                        pass

            return StreamingResponse(
                stream_generator(),
                status_code=status,
                media_type=content_type,
                headers=headers_out,
            )
        except HTTPException:
            try:
                await client.aclose()
            except Exception:
                pass
            raise
        except Exception as e:
            try:
                await client.aclose()
            except Exception:
                pass
            log.exception("Failed to proxy mask file %s -> %s", report_id, e)
            raise HTTPException(status_code=502, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Failed to proxy mask file %s -> %s", report_id, e)
        raise HTTPException(status_code=502, detail=str(e))
