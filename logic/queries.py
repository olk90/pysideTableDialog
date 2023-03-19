"""
This file contains all queries needed by the dialogs
to access data in the database and show it in the
respective dialog.
"""


def person_query(search: str) -> str:
    query = """
        select
            p.id,
            p.firstname,
            p.lastname,
            p.email
        from Person p
        where
            p.firstname like '%{search}%'
            or p.lastname like '%{search}%'
            or p.email like '%{search}%'
    """.format(search=search)
    return query


def inventory_query(search: str) -> str:
    query = """
        select 
            i.id,
            i.category,
            i.name,
            i.available,
            i.lending_date,
            p.firstname || ' ' || p.lastname,
            i.next_mot
        from InventoryItem i
        left outer join Person p on i.lender_id = p.id
        where
            i.name like '%{search}%'
            or i.category like '%{search}%'
            or p.firstname like '%{search}%'
            or p.lastname like '%{search}%'
    """.format(search=search)
    return query


def person_fullname_query() -> str:
    query = """
        select
            p.firstname || ' ' || p.lastname as name,
            p.id 
        from Person p
        order by p.lastname, p.firstname
        """
    return query
