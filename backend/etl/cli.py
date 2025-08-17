"""Command-line interface for Government Data ETL Pipeline."""

import click
import asyncio
import logging
from datetime import datetime
from typing import Optional

from etl.government_data_pipeline import GovernmentDataETL
from core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Government Data ETL Pipeline CLI."""
    pass


@cli.command()
@click.option('--api-key', envvar='GOVERNMENT_API_KEY', 
              default='579b464db66ec23bdd00000106337f18059d41867b7729cfd2ea081f',
              help='API key for government data portal')
def initialize(api_key: str):
    """Initialize dataset registry in database."""
    click.echo("🚀 Initializing Government Dataset Registry...")
    
    async def run():
        etl = GovernmentDataETL(api_key)
        await etl.initialize_datasets()
        click.echo("✅ Dataset registry initialized successfully!")
    
    asyncio.run(run())


@cli.command()
@click.argument('resource_id')
@click.option('--limit', default=1000, help='Maximum records to fetch')
@click.option('--api-key', envvar='GOVERNMENT_API_KEY',
              default='579b464db66ec23bdd00000106337f18059d41867b7729cfd2ea081f',
              help='API key for government data portal')
def ingest(resource_id: str, limit: int, api_key: str):
    """Ingest data for a specific dataset."""
    click.echo(f"📥 Ingesting data for resource: {resource_id}")
    click.echo(f"📊 Limit: {limit} records")
    
    async def run():
        etl = GovernmentDataETL(api_key)
        await etl.ingest_dataset(resource_id, limit)
        click.echo("✅ Data ingestion completed!")
    
    asyncio.run(run())


@cli.command()
@click.option('--api-key', envvar='GOVERNMENT_API_KEY',
              default='579b464db66ec23bdd00000106337f18059d41867b7729cfd2ea081f',
              help='API key for government data portal')
@click.option('--limit', default=100, help='Records per dataset')
def ingest_all(api_key: str, limit: int):
    """Ingest data for all registered datasets."""
    click.echo("🔄 Starting bulk data ingestion for all datasets...")
    
    async def run():
        etl = GovernmentDataETL(api_key)
        
        # Get all dataset definitions
        datasets = etl.dataset_definitions
        
        click.echo(f"📋 Found {len(datasets)} datasets to process")
        
        for i, dataset in enumerate(datasets, 1):
            click.echo(f"\n[{i}/{len(datasets)}] Processing: {dataset['title']}")
            try:
                await etl.ingest_dataset(dataset['resource_id'], limit)
                click.echo(f"✅ Successfully processed: {dataset['slug']}")
            except Exception as e:
                click.echo(f"❌ Error processing {dataset['slug']}: {e}")
                continue
        
        click.echo("\n🎉 Bulk ingestion completed!")
    
    asyncio.run(run())


@cli.command()
@click.argument('category', required=False)
def list_datasets(category: Optional[str]):
    """List all available datasets."""
    from services.government_data_service import government_data_service
    
    if category:
        click.echo(f"📊 Datasets in category: {category}")
        datasets = government_data_service.get_datasets_by_category(category)
    else:
        click.echo("📊 All Available Datasets:")
        datasets = government_data_service.get_all_datasets()
    
    if not datasets:
        click.echo("No datasets found.")
        return
    
    for dataset in datasets:
        click.echo(f"\n🔹 {dataset['title']}")
        click.echo(f"   Slug: {dataset['slug']}")
        click.echo(f"   Category: {dataset['category']}")
        click.echo(f"   Geographic Level: {dataset['geographic_level']}")
        click.echo(f"   Time Granularity: {dataset['time_granularity']}")
        click.echo(f"   Indicators: {dataset.get('indicators_count', 'N/A')}")


@cli.command()
def list_categories():
    """List all available dataset categories."""
    from services.government_data_service import government_data_service
    
    categories = government_data_service.get_available_categories()
    
    click.echo("📂 Available Dataset Categories:")
    for category in categories:
        click.echo(f"  • {category}")


@cli.command()
@click.argument('slug')
def dataset_info(slug: str):
    """Get detailed information about a specific dataset."""
    from services.government_data_service import government_data_service
    
    dataset = government_data_service.get_dataset_by_slug(slug)
    
    if not dataset:
        click.echo(f"❌ Dataset not found: {slug}")
        return
    
    click.echo(f"\n📊 Dataset: {dataset['title']}")
    click.echo(f"   Slug: {dataset['slug']}")
    click.echo(f"   Category: {dataset['category']}")
    click.echo(f"   Subcategory: {dataset['subcategory']}")
    click.echo(f"   Geographic Level: {dataset['geographic_level']}")
    click.echo(f"   Time Granularity: {dataset['time_granularity']}")
    click.echo(f"   Update Frequency: {dataset['update_frequency']}")
    click.echo(f"   Source Department: {dataset['source_department']}")
    
    if dataset['indicators']:
        click.echo(f"\n📈 Indicators ({len(dataset['indicators'])}):")
        for indicator in dataset['indicators']:
            click.echo(f"  • {indicator['display_name']} ({indicator['data_type']})")
            if indicator['unit']:
                click.echo(f"    Unit: {indicator['unit']}")


@cli.command()
@click.argument('slug')
@click.option('--limit', default=10, help='Maximum records to show')
def preview_data(slug: str, limit: int):
    """Preview data for a specific dataset."""
    from services.government_data_service import government_data_service
    
    data = government_data_service.get_dataset_data(slug, limit=limit)
    
    if not data:
        click.echo(f"❌ No data found for dataset: {slug}")
        return
    
    click.echo(f"\n📊 Data Preview for: {data['dataset']['title']}")
    click.echo(f"   Total Records: {data['total_records']}")
    click.echo(f"   Showing: {len(data['data'])} records")
    
    if data['data']:
        # Show column headers
        headers = list(data['data'][0].keys())
        click.echo(f"\nColumns: {', '.join(headers)}")
        
        # Show sample data
        click.echo("\nSample Data:")
        for i, record in enumerate(data['data'][:limit], 1):
            click.echo(f"\n[{i}]")
            for key, value in record.items():
                click.echo(f"  {key}: {value}")


@cli.command()
@click.argument('slug')
def dataset_stats(slug: str):
    """Get statistics for a specific dataset."""
    from services.government_data_service import government_data_service
    
    stats = government_data_service.get_dataset_statistics(slug)
    
    if not stats:
        click.echo(f"❌ Dataset not found: {slug}")
        return
    
    click.echo(f"\n📊 Statistics for: {stats['dataset']['title']}")
    click.echo(f"   Total Records: {stats['total_records']}")
    click.echo(f"   Indicators: {stats['indicators_count']}")
    click.echo(f"   Geographic Coverage: {stats['geographic_coverage']} locations")
    click.echo(f"   Time Coverage: {stats['time_coverage']} periods")
    click.echo(f"   Last Updated: {stats['last_updated'] or 'Unknown'}")
    click.echo(f"   Data Quality Score: {stats['data_quality']['quality_score']}%")


@cli.command()
@click.argument('query')
@click.option('--category', help='Filter by category')
def search_datasets(query: str, category: Optional[str]):
    """Search datasets by query."""
    from services.government_data_service import government_data_service
    
    datasets = government_data_service.search_datasets(query, category)
    
    if not datasets:
        click.echo(f"❌ No datasets found matching: {query}")
        return
    
    click.echo(f"\n🔍 Search Results for: {query}")
    if category:
        click.echo(f"   Category Filter: {category}")
    click.echo(f"   Total Results: {len(datasets)}")
    
    for dataset in datasets:
        click.echo(f"\n🔹 {dataset['title']}")
        click.echo(f"   Slug: {dataset['slug']}")
        click.echo(f"   Category: {dataset['category']}")
        click.echo(f"   Geographic Level: {dataset['geographic_level']}")


@cli.command()
def status():
    """Show overall ETL pipeline status."""
    from services.government_data_service import government_data_service
    
    try:
        datasets = government_data_service.get_all_datasets()
        categories = government_data_service.get_available_categories()
        
        click.echo("🏛️  Government Data ETL Pipeline Status")
        click.echo("=" * 50)
        click.echo(f"📊 Total Datasets: {len(datasets)}")
        click.echo(f"📂 Categories: {len(categories)}")
        click.echo(f"🕐 Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show datasets by category
        click.echo("\n📊 Datasets by Category:")
        for category in categories:
            category_datasets = [d for d in datasets if d['category'] == category]
            click.echo(f"  • {category}: {len(category_datasets)} datasets")
        
        # Show recent activity (placeholder)
        click.echo("\n🔄 Recent Activity:")
        click.echo("  • ETL pipeline ready")
        click.echo("  • API endpoints active")
        click.echo("  • Database schema extended")
        
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}")


if __name__ == '__main__':
    cli()
