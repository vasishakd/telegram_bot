from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


class InvalidRequest(Exception):
    pass


async def send_shikimori(
    text: str | None = None,
    ids: list[str] | None = None,
    limit: int = 1,
) -> dict:
    transport = AIOHTTPTransport(url='https://shikimori.one/api/graphql')

    query = []

    if text:
        query.append(f'search: "{text}"')

    if ids:
        query.append(f'ids: "{",".join(ids)}"')

    if not query:
        raise InvalidRequest('No query was provided')

    query = ', '.join(query)

    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:
        query = gql(
            f"""
                {{
                  animes({query}, limit: {limit}) {{
                    id
                    malId
                    name
                    russian
                    licenseNameRu
                    english
                    japanese
                    synonyms
                    kind
                    rating
                    score
                    status
                    episodes
                    episodesAired
                    duration
                    airedOn {{ year month day date }}
                    releasedOn {{ year month day date }}
                    url
                    season

                    poster {{ id originalUrl mainUrl }}

                    fansubbers
                    fandubbers
                    licensors
                    createdAt,
                    updatedAt,
                    nextEpisodeAt,
                    isCensored
                  }}
                }}
                """
        )

        return await session.execute(query)
