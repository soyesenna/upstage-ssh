import click
from tabulate import tabulate
from src.util.config_util import load_config

def search_in_items(items, query, item_type):
    results = []
    query_lower = query.lower()
    
    for item in items:
        if item_type == 'hosts':
            value_field = 'address'
        elif item_type == 'keypairs':
            value_field = 'path'
        else:
            value_field = 'value'
        
        alias_match = query_lower in str(item.get('alias', '')).lower()
        value_match = query_lower in str(item.get(value_field, '')).lower()
        
        if alias_match or value_match:
            results.append({
                'type': item_type.rstrip('s'),
                'alias': item['alias'],
                'value': item.get(value_field)
            })
    
    return results

def print_search_results(results, query):
    if not results:
        click.echo(f"No results found for query: '{query}'")
        return
    
    table_data = []
    for result in results:
        if result['type'] == 'password':
            value_display = '****'
        else:
            value_display = result['value']
        
        table_data.append([
            result['type'].upper(),
            result['alias'],
            value_display
        ])
    
    click.echo(f"\nSearch results for '{query}':")
    click.echo(tabulate(table_data, headers=['Type', 'Alias', 'Value'], tablefmt='grid'))
    click.echo(f"\nTotal: {len(results)} result(s) found")

@click.group(invoke_without_command=True)
@click.option('--query', '-q', required=False, help='Search query for value or alias')
@click.pass_context
def find(ctx, query):
    """Search for stored SSH connection information by value or alias."""
    if ctx.invoked_subcommand is None:
        if not query:
            click.echo("Error: Please provide a search query with --query or -q option")
            click.echo("Example: ussh find --query myserver")
            return
        
        config = load_config()
        all_results = []
        
        for category in ['hosts', 'ports', 'usernames', 'passwords', 'keypairs']:
            items = config.get(category, [])
            results = search_in_items(items, query, category)
            all_results.extend(results)
        
        print_search_results(all_results, query)

@click.command()
@click.option('--query', '-q', required=True, help='Search query for host address or alias')
def host(query):
    config = load_config()
    hosts = config.get('hosts', [])
    results = search_in_items(hosts, query, 'hosts')
    print_search_results(results, query)

@click.command()
@click.option('--query', '-q', required=True, help='Search query for port value or alias')
def port(query):
    config = load_config()
    ports = config.get('ports', [])
    results = search_in_items(ports, query, 'ports')
    print_search_results(results, query)

@click.command()
@click.option('--query', '-q', required=True, help='Search query for username value or alias')
def username(query):
    config = load_config()
    usernames = config.get('usernames', [])
    results = search_in_items(usernames, query, 'usernames')
    print_search_results(results, query)

@click.command()
@click.option('--query', '-q', required=True, help='Search query for password alias')
def password(query):
    config = load_config()
    passwords = config.get('passwords', [])
    results = search_in_items(passwords, query, 'passwords')
    print_search_results(results, query)

@click.command()
@click.option('--query', '-q', required=True, help='Search query for keypair path or alias')
def keypair(query):
    config = load_config()
    keypairs = config.get('keypairs', [])
    results = search_in_items(keypairs, query, 'keypairs')
    print_search_results(results, query)

@click.command()
@click.option('--query', '-q', required=True, help='Search query for environment alias')
def environment(query):
    config = load_config()
    environments = config.get('environments', [])
    results = search_in_items(environments, query, 'environments')
    print_search_results(results, query)

find.add_command(host)

find.add_command(port)

find.add_command(username)
find.add_command(username, name='user')

find.add_command(password)
find.add_command(password, name='pwd')

find.add_command(keypair)
find.add_command(keypair, name='kp')

find.add_command(environment)
find.add_command(environment, name='env')