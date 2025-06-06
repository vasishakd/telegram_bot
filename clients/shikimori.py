from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


async def send_shikimori(text: str):
    transport = AIOHTTPTransport(url="https://shikimori.one/api/graphql")

    # Using `async with` on the client will start a connection on the transport
    # and provide a `session` variable to execute queries on this connection
    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:
        # Execute single query
        query = gql(
            f"""
                {{
                  animes(search: "{text}", limit: 6) {{
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