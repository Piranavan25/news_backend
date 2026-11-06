from urllib.parse import (
    parse_qsl,
    quote,
    urlencode,
    urlsplit,
    urlunsplit,
)


TRACKING_PARAMETERS = {
    "fbclid",
    "gclid",
    "dclid",
    "msclkid",
    "ref",
    "source",
}


def normalize_url(url: str) -> str:
    """
    Normalize an article URL by:
    - Removing fragments.
    - Removing tracking query parameters.
    - Removing default HTTP/HTTPS ports.
    - Removing trailing slashes from the path.
    """

    parsed = urlsplit(url.strip())

    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()

    if not scheme or not hostname:
        raise ValueError(f"Invalid URL: {url}")

    # Preserve non-default ports.
    port = parsed.port

    if port and not (
        (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
    ):
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    # Remove common tracking parameters.
    query_parameters = [
        (key, value)
        for key, value in parse_qsl(
            parsed.query,
            keep_blank_values=True,
        )
        if key.lower() not in TRACKING_PARAMETERS
        and not key.lower().startswith("utm_")
    ]

    normalized_query = urlencode(query_parameters)

    path = quote(
    parsed.path.rstrip("/"),
    safe="/%:@!$&'()*+,;=-._~",
)

    return urlunsplit((
        scheme,
        netloc,
        path,
        normalized_query,
        "",
    ))