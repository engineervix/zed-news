#!/usr/bin/env python3
"""
Foreign Exchange data update script
Updates FX rates data for the zed-news website
"""

import logging
import time

from colorama import init
from dotenv import load_dotenv

from app.core.fx.processor import update_fx_data
from app.core.utilities import configure_logging


def main():
    """Update FX data for the website"""
    start_time = time.time()

    # Configure logging
    init()
    configure_logging()

    # Load environment variables
    load_dotenv()

    logging.info("Starting FX data update...")

    try:
        # Update FX data
        fx_data = update_fx_data()

        # Log summary
        current_rates = fx_data.get("current_rates", {}).get("rates", {})
        logging.info("FX rates updated successfully:")
        for currency, rates in current_rates.items():
            logging.info(f"  {currency}: {rates['mid']:.3f} ZMW")

        end_time = time.time()
        elapsed = end_time - start_time
        logging.info(f"FX data update completed in {elapsed:.2f} seconds")

    except Exception as e:
        logging.error(f"FX data update failed: {e}")
        raise


if __name__ == "__main__":
    main()
