# Standard Library
from typing import Optional

# First Party
from config.etl_config import ETLIndexes


def movie_index_sql_script(load_from: Optional[str]) -> str:

    return f"""
        SELECT
           fw.id,
           fw.title,
           fw.description,
           fw.rating AS imdb_rating,
           COALESCE(
            JSON_AGG(
                   DISTINCT p.full_name)
                   FILTER (WHERE p.id is not null AND pfw.role = 'director'), '[]') AS director,
           COALESCE(
            JSON_AGG(
                   DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
                   FILTER (WHERE p.id is not null AND pfw.role = 'actor'), '[]') AS actors,
           COALESCE(
            JSON_AGG(
                   DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name))
                   FILTER (WHERE p.id is not null AND pfw.role = 'writer'), '[]') AS writers,
           COALESCE(
            JSON_AGG(DISTINCT p.full_name)
               FILTER (WHERE p.id is not null AND pfw.role = 'actor'), '[]') AS actors_names,
           COALESCE(
            JSON_AGG(DISTINCT p.full_name)
               FILTER (WHERE p.id is not null AND pfw.role = 'writer'), '[]') AS writers_names,
           COALESCE(
            JSON_AGG(DISTINCT g.name), '[]') AS genre,
           fw.updated_at AS modified
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        LEFT JOIN content.person p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre g ON g.id = gfw.genre_id
        WHERE fw.updated_at > '{load_from}'
        GROUP BY fw.id
        ORDER BY fw.updated_at ASC;
        """


def get_query_by_index(index: str, load_from: Optional[str]) -> str:

    if not index:
        raise ValueError("No country (script) for old index {index}")

    elif index == ETLIndexes.movies:
        return movie_index_sql_script(load_from)
