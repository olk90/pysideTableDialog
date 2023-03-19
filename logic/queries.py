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


def lending_history_query(search: str) -> str:
    query = """
        select 
            l.id,
            i.name,
            p.firstname || ' ' || p.lastname,
            l.lending_date,
            l.return_date
        from LendingHistory l
        inner join Person p on l.lender_id = p.id
        inner join InventoryItem i on l.item_id = i.id
        where
            i.name like '%{search}%'
            or p.firstname like '%{search}%'
            or p.lastname like '%{search}%'
        order by p.lastname, p.firstname, l.lending_date, l.return_date
    """.format(search=search)
    return query
