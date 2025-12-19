"""
Standard test cases for NL2SQL benchmark.
M10: Comprehensive test suite covering various query types.
"""
from eval.benchmark import BenchmarkCase


def get_all_test_cases():
    """Get complete test suite"""
    return (
        get_simple_select_cases() +
        get_aggregate_cases() +
        get_filter_cases() +
        get_sort_cases() +
        get_join_cases() +
        get_group_by_cases() +
        get_complex_cases()
    )


def get_simple_select_cases():
    """Simple SELECT queries"""
    return [
        BenchmarkCase(
            question="显示所有专辑",
            expected_sql="SELECT * FROM Album",
            category="simple_select",
            description="SELECT all from single table"
        ),
        BenchmarkCase(
            question="显示所有客户",
            expected_sql="SELECT * FROM Customer",
            category="simple_select",
            description="SELECT all customers"
        ),
        BenchmarkCase(
            question="显示前10首歌曲",
            expected_sql="SELECT * FROM Track LIMIT 10",
            expected_result_count=10,
            category="simple_select",
            description="SELECT with LIMIT"
        ),
        BenchmarkCase(
            question="显示所有音乐风格",
            expected_sql="SELECT * FROM Genre",
            category="simple_select",
            description="SELECT genres"
        ),
        BenchmarkCase(
            question="列出所有艺术家",
            expected_sql="SELECT * FROM Artist",
            category="simple_select",
            description="SELECT artists"
        )
    ]


def get_aggregate_cases():
    """Aggregation queries (COUNT, SUM, AVG, etc.)"""
    return [
        BenchmarkCase(
            question="有多少首歌曲？",
            expected_sql="SELECT COUNT(*) as total FROM Track",
            expected_result_count=1,
            category="aggregate",
            description="COUNT all tracks"
        ),
        BenchmarkCase(
            question="统计客户总数",
            expected_sql="SELECT COUNT(*) as total FROM Customer",
            expected_result_count=1,
            category="aggregate",
            description="COUNT customers"
        ),
        BenchmarkCase(
            question="有多少张专辑？",
            expected_sql="SELECT COUNT(*) as total FROM Album",
            expected_result_count=1,
            category="aggregate",
            description="COUNT albums"
        ),
        BenchmarkCase(
            question="歌曲的平均价格是多少？",
            expected_sql="SELECT AVG(UnitPrice) as avg_price FROM Track",
            expected_result_count=1,
            category="aggregate",
            description="AVG price"
        ),
        BenchmarkCase(
            question="统计所有订单的总金额",
            expected_sql="SELECT SUM(Total) as total_amount FROM Invoice",
            expected_result_count=1,
            category="aggregate",
            description="SUM invoice totals"
        )
    ]


def get_filter_cases():
    """Queries with WHERE clause"""
    return [
        BenchmarkCase(
            question="显示来自巴西的客户",
            expected_sql="SELECT * FROM Customer WHERE Country = 'Brazil'",
            category="filter",
            description="WHERE with string equality"
        ),
        BenchmarkCase(
            question="显示价格大于1美元的歌曲",
            expected_sql="SELECT * FROM Track WHERE UnitPrice > 1",
            category="filter",
            description="WHERE with numeric comparison"
        ),
        BenchmarkCase(
            question="显示Rock风格的歌曲",
            expected_sql="SELECT t.* FROM Track t JOIN Genre g ON t.GenreId = g.GenreId WHERE g.Name = 'Rock'",
            category="filter",
            description="WHERE with join"
        ),
        BenchmarkCase(
            question="显示价格在0.99到1.99之间的歌曲",
            expected_sql="SELECT * FROM Track WHERE UnitPrice BETWEEN 0.99 AND 1.99",
            category="filter",
            description="WHERE with BETWEEN"
        ),
        BenchmarkCase(
            question="显示2010年的所有订单",
            expected_sql="SELECT * FROM Invoice WHERE InvoiceDate LIKE '2010%'",
            category="filter",
            description="WHERE with date filter"
        )
    ]


def get_sort_cases():
    """Queries with ORDER BY"""
    return [
        BenchmarkCase(
            question="按价格降序排列所有歌曲",
            expected_sql="SELECT * FROM Track ORDER BY UnitPrice DESC",
            category="sort",
            description="ORDER BY DESC"
        ),
        BenchmarkCase(
            question="按名字排序显示所有艺术家",
            expected_sql="SELECT * FROM Artist ORDER BY Name",
            category="sort",
            description="ORDER BY ASC"
        ),
        BenchmarkCase(
            question="价格最高的10首歌曲",
            expected_sql="SELECT * FROM Track ORDER BY UnitPrice DESC LIMIT 10",
            expected_result_count=10,
            category="sort",
            description="Top N with ORDER BY"
        ),
        BenchmarkCase(
            question="时长最长的5首歌曲",
            expected_sql="SELECT Name, Milliseconds FROM Track ORDER BY Milliseconds DESC LIMIT 5",
            expected_result_count=5,
            category="sort",
            description="Top N by duration"
        ),
        BenchmarkCase(
            question="最新的10个订单",
            expected_sql="SELECT * FROM Invoice ORDER BY InvoiceDate DESC LIMIT 10",
            expected_result_count=10,
            category="sort",
            description="Latest records"
        )
    ]


def get_join_cases():
    """Queries with JOIN"""
    return [
        BenchmarkCase(
            question="显示所有专辑及其艺术家名称",
            expected_sql="SELECT al.Title, ar.Name FROM Album al JOIN Artist ar ON al.ArtistId = ar.ArtistId",
            category="join",
            description="Simple JOIN"
        ),
        BenchmarkCase(
            question="AC/DC的所有专辑",
            expected_sql="SELECT al.Title FROM Album al JOIN Artist ar ON al.ArtistId = ar.ArtistId WHERE ar.Name = 'AC/DC'",
            category="join",
            description="JOIN with WHERE"
        ),
        BenchmarkCase(
            question="显示所有歌曲及其专辑和艺术家",
            expected_sql="SELECT t.Name as Track, al.Title as Album, ar.Name as Artist FROM Track t JOIN Album al ON t.AlbumId = al.AlbumId JOIN Artist ar ON al.ArtistId = ar.ArtistId",
            category="join",
            description="Multiple JOINs"
        ),
        BenchmarkCase(
            question="显示每个客户的订单总数",
            expected_sql="SELECT c.FirstName, c.LastName, COUNT(i.InvoiceId) as order_count FROM Customer c LEFT JOIN Invoice i ON c.CustomerId = i.CustomerId GROUP BY c.CustomerId, c.FirstName, c.LastName",
            category="join",
            description="JOIN with GROUP BY"
        )
    ]


def get_group_by_cases():
    """Queries with GROUP BY"""
    return [
        BenchmarkCase(
            question="每个国家有多少客户？",
            expected_sql="SELECT Country, COUNT(*) as customer_count FROM Customer GROUP BY Country",
            category="group_by",
            description="GROUP BY with COUNT"
        ),
        BenchmarkCase(
            question="每个音乐风格有多少首歌？",
            expected_sql="SELECT g.Name, COUNT(t.TrackId) as track_count FROM Genre g LEFT JOIN Track t ON g.GenreId = t.GenreId GROUP BY g.GenreId, g.Name",
            category="group_by",
            description="GROUP BY with JOIN"
        ),
        BenchmarkCase(
            question="统计每个艺术家的专辑数",
            expected_sql="SELECT ar.Name, COUNT(al.AlbumId) as album_count FROM Artist ar LEFT JOIN Album al ON ar.ArtistId = al.ArtistId GROUP BY ar.ArtistId, ar.Name",
            category="group_by",
            description="Artist album counts"
        ),
        BenchmarkCase(
            question="每个城市的客户数量",
            expected_sql="SELECT City, COUNT(*) as customer_count FROM Customer GROUP BY City",
            category="group_by",
            description="GROUP BY city"
        ),
        BenchmarkCase(
            question="每年的订单总金额",
            expected_sql="SELECT strftime('%Y', InvoiceDate) as year, SUM(Total) as total_amount FROM Invoice GROUP BY year",
            category="group_by",
            description="GROUP BY year with SUM"
        )
    ]


def get_complex_cases():
    """Complex queries combining multiple features"""
    return [
        BenchmarkCase(
            question="消费金额最高的10个客户",
            expected_sql="SELECT c.FirstName, c.LastName, SUM(i.Total) as total_spent FROM Customer c JOIN Invoice i ON c.CustomerId = i.CustomerId GROUP BY c.CustomerId, c.FirstName, c.LastName ORDER BY total_spent DESC LIMIT 10",
            expected_result_count=10,
            category="complex",
            description="Top customers by spending"
        ),
        BenchmarkCase(
            question="每个国家客户的平均消费",
            expected_sql="SELECT c.Country, AVG(i.Total) as avg_spending FROM Customer c JOIN Invoice i ON c.CustomerId = i.CustomerId GROUP BY c.Country",
            category="complex",
            description="Average spending by country"
        ),
        BenchmarkCase(
            question="歌曲数量最多的前5个音乐风格",
            expected_sql="SELECT g.Name, COUNT(t.TrackId) as track_count FROM Genre g JOIN Track t ON g.GenreId = t.GenreId GROUP BY g.GenreId, g.Name ORDER BY track_count DESC LIMIT 5",
            expected_result_count=5,
            category="complex",
            description="Top genres by track count"
        ),
        BenchmarkCase(
            question="销量最好的前10首歌",
            expected_sql="SELECT t.Name, COUNT(il.InvoiceLineId) as sales_count FROM Track t JOIN InvoiceLine il ON t.TrackId = il.TrackId GROUP BY t.TrackId, t.Name ORDER BY sales_count DESC LIMIT 10",
            expected_result_count=10,
            category="complex",
            description="Best selling tracks"
        ),
        BenchmarkCase(
            question="专辑数量超过10的艺术家",
            expected_sql="SELECT ar.Name, COUNT(al.AlbumId) as album_count FROM Artist ar JOIN Album al ON ar.ArtistId = al.ArtistId GROUP BY ar.ArtistId, ar.Name HAVING COUNT(al.AlbumId) > 10",
            category="complex",
            description="Artists with HAVING clause"
        )
    ]


def get_test_cases_by_category(category: str):
    """Get test cases for a specific category"""
    category_map = {
        "simple_select": get_simple_select_cases,
        "aggregate": get_aggregate_cases,
        "filter": get_filter_cases,
        "sort": get_sort_cases,
        "join": get_join_cases,
        "group_by": get_group_by_cases,
        "complex": get_complex_cases
    }
    
    if category in category_map:
        return category_map[category]()
    else:
        return []


if __name__ == "__main__":
    """Display test case summary"""
    all_cases = get_all_test_cases()
    
    print("="*70)
    print("NL2SQL Benchmark Test Cases")
    print("="*70)
    
    # Count by category
    from collections import Counter
    category_counts = Counter(case.category for case in all_cases)
    
    print(f"\nTotal Test Cases: {len(all_cases)}\n")
    print("By Category:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")
    
    print("\n" + "="*70)
    print("Sample Test Cases:")
    print("="*70)
    
    # Show first 3 cases
    for i, case in enumerate(all_cases[:3], 1):
        print(f"\n{i}. [{case.category}] {case.description}")
        print(f"   Q: {case.question}")
        print(f"   SQL: {case.expected_sql}")
