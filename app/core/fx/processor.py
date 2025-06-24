#!/usr/bin/env python3
"""
Zambia Kwacha FX Rates Data Processor
Fetches, processes, and normalizes historical FX rates from Bank of Zambia
Adapted for integration with zed-news project
"""

import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import requests

# Configure logging
logger = logging.getLogger(__name__)


class FXDataProcessor:
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize FX data processor

        Args:
            data_dir: Directory to store FX data. Defaults to project data/fx/
        """
        if data_dir is None:
            # Default to project data directory
            project_root = Path(__file__).parent.parent.parent.parent
            data_dir = project_root / "data" / "fx"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Web data directory for static files
        self.web_data_dir = Path(__file__).parent.parent.parent / "web" / "_data"
        self.web_data_dir.mkdir(parents=True, exist_ok=True)

        # Bank of Zambia data source
        self.url = "https://www.boz.zm/AVERAGE_FXRATES.xlsx"

        # Rebasing cutoff date (when Kwacha was rebased)
        self.rebase_date = date(2013, 1, 1)

        # Supported currencies
        self.currencies = ["USD", "GBP", "EUR", "ZAR"]

    def fetch_data(self) -> bytes:
        """Download the Excel file from Bank of Zambia"""
        logger.info("Fetching FX data from Bank of Zambia...")
        try:
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()

            # Save raw file for backup
            raw_file = self.data_dir / f"raw_fx_data_{datetime.now().strftime('%Y%m%d')}.xlsx"
            with open(raw_file, "wb") as f:
                f.write(response.content)

            logger.info(f"Raw data saved to {raw_file}")
            return response.content

        except requests.RequestException as e:
            logger.error(f"Failed to fetch FX data: {e}")
            raise

    def _setup_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Set up proper column names for the Excel data"""
        if len(df.columns) >= 10:
            df.columns = [
                "empty_col",  # Column A is empty
                "date",  # Column B has dates
                "usd_buy",  # Column C - Dollar Buy
                "usd_sale",  # Column D - Dollar Sale
                "gbp_buy",  # Column E - Pound Buy
                "gbp_sale",  # Column F - Pound Sale
                "eur_buy",  # Column G - Euro Buy
                "eur_sale",  # Column H - Euro Sale
                "zar_buy",  # Column I - Rand Buy
                "zar_sale",  # Column J - Rand Sale
            ] + [f"extra_col_{i}" for i in range(len(df.columns) - 10)]
        else:
            # Handle case with fewer columns
            base_columns = [
                "empty_col",
                "date",
                "usd_buy",
                "usd_sale",
                "gbp_buy",
                "gbp_sale",
                "eur_buy",
                "eur_sale",
                "zar_buy",
                "zar_sale",
            ]
            df.columns = base_columns[: len(df.columns)]

        # Drop the empty first column if it exists
        if "empty_col" in df.columns:
            df = df.drop("empty_col", axis=1)

        return df

    def _convert_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert date column to proper datetime format"""

        def convert_date(date_val):
            if pd.isna(date_val):
                return None
            if isinstance(date_val, (int, float)):
                # Handle Excel serial numbers (like 43649, 43650)
                if 40000 <= date_val <= 50000:  # Reasonable range for Excel dates 2009-2037
                    return pd.to_datetime(date_val, origin="1899-12-30", unit="D")
                else:
                    return None
            elif isinstance(date_val, datetime):
                return date_val
            else:
                # Try to parse as string
                try:
                    return pd.to_datetime(date_val)
                except Exception:
                    return None

        df["date"] = df["date"].apply(convert_date)
        df = df[df["date"].notna()].copy()
        return df

    def _clean_currency_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate currency data"""
        numeric_cols = ["usd_buy", "usd_sale", "gbp_buy", "gbp_sale", "eur_buy", "eur_sale", "zar_buy", "zar_sale"]
        existing_numeric_cols = [col for col in numeric_cols if col in df.columns]

        # Convert to numeric
        for col in existing_numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Filter out corrupted USD data (most critical)
        if "usd_buy" in df.columns and "usd_sale" in df.columns:
            valid_mask = (
                (df["usd_buy"].notna())
                & (df["usd_sale"].notna())
                & (df["usd_buy"] > 0)
                & (df["usd_sale"] > 0)
                & (df["usd_buy"] < 50000)
                & (df["usd_sale"] > 1)  # Remove Excel serial numbers
                & ((df["usd_sale"] / df["usd_buy"]) < 2.0)  # Reasonable spread
                & ((df["usd_buy"] / df["usd_sale"]) < 2.0)
            )

            logger.info(f"Filtering out {(~valid_mask).sum()} corrupted rows")
            df = df[valid_mask].copy()

        # Clean other currency columns (set bad values to NaN)
        for currency in ["gbp", "eur", "zar"]:
            buy_col, sale_col = f"{currency}_buy", f"{currency}_sale"

            if buy_col in df.columns and sale_col in df.columns:
                currency_mask = (df[buy_col].isna()) | (
                    (df[buy_col] > 0)
                    & (df[sale_col] > 0)
                    & (df[buy_col] < 50000)
                    & ((df[sale_col] / df[buy_col]) < 2.0)
                    & ((df[buy_col] / df[sale_col]) < 2.0)
                )

                bad_rows = (~currency_mask).sum()
                if bad_rows > 0:
                    logger.info(f"Cleaning {bad_rows} corrupted {currency.upper()} rows")
                    df.loc[~currency_mask, [buy_col, sale_col]] = pd.NA

        return df

    def process_excel_data(self, excel_content: bytes) -> pd.DataFrame:
        """Process the Excel data and normalize pre-2013 values"""
        logger.info("Processing Excel data...")

        try:
            from io import BytesIO

            # Read Excel file with proper header handling
            # Skip rows 1-11: rows 1-4 are headers, rows 5-11 contain corrupted data
            df = pd.read_excel(
                BytesIO(excel_content),
                sheet_name=0,  # First sheet
                skiprows=11,  # Skip the first 11 rows (headers + corrupted data)
                header=None,  # We'll set headers manually
            )

            logger.info(f"Excel data has {len(df.columns)} columns")

            # Process data through helper methods
            df = self._setup_column_names(df)
            df = df[df["date"].notna()].copy()  # Remove rows with no date
            df = self._convert_dates(df)
            df = self._clean_currency_data(df)

            # Finalize datetime columns
            df["date"] = pd.to_datetime(df["date"])
            df["date_only"] = df["date"].dt.date

            logger.info(f"Processed {len(df)} data points from {df['date'].min()} to {df['date'].max()}")
            return df

        except Exception as e:
            logger.error(f"Failed to process Excel data: {e}")
            raise

    def normalize_pre_rebase_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize pre-2013 data by dividing by 1000"""
        logger.info("Normalizing pre-rebase data...")

        # Identify pre-rebase data
        pre_rebase_mask = df["date_only"] < self.rebase_date
        pre_rebase_count = pre_rebase_mask.sum()

        logger.info(f"Found {pre_rebase_count} pre-rebase records to normalize")

        # Currency columns to normalize
        currency_cols = ["usd_buy", "usd_sale", "gbp_buy", "gbp_sale", "eur_buy", "eur_sale", "zar_buy", "zar_sale"]

        # Filter currency columns to only those that exist in the dataframe
        existing_currency_cols = [col for col in currency_cols if col in df.columns]

        # Normalize pre-rebase data
        for col in existing_currency_cols:
            # Ensure the column is numeric before division
            if df[col].dtype in ["object", "datetime64[ns]"]:
                # Try to convert to numeric, coercing errors to NaN
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Only normalize if column contains numeric data
            if pd.api.types.is_numeric_dtype(df[col]):
                df.loc[pre_rebase_mask, col] = df.loc[pre_rebase_mask, col] / 1000

        # Add flag to indicate normalized data
        df["normalized"] = pre_rebase_mask

        return df

    def generate_web_data(self, df: pd.DataFrame) -> Dict:
        """Generate web-friendly JSON data for the frontend"""
        logger.info("Generating web data...")

        # Sort by date
        df_sorted = df.sort_values("date_only")

        # Generate current rates (latest available)
        latest_date = df_sorted["date_only"].max()
        latest_data = df_sorted[df_sorted["date_only"] == latest_date].iloc[0]

        current_rates = {
            "date": latest_date.isoformat(),
            "rates": {
                "USD": {
                    "buy": float(latest_data["usd_buy"]),
                    "sell": float(latest_data["usd_sale"]),
                    "mid": float((latest_data["usd_buy"] + latest_data["usd_sale"]) / 2),
                },
                "GBP": {
                    "buy": float(latest_data["gbp_buy"]),
                    "sell": float(latest_data["gbp_sale"]),
                    "mid": float((latest_data["gbp_buy"] + latest_data["gbp_sale"]) / 2),
                },
                "EUR": {
                    "buy": float(latest_data["eur_buy"]),
                    "sell": float(latest_data["eur_sale"]),
                    "mid": float((latest_data["eur_buy"] + latest_data["eur_sale"]) / 2),
                },
                "ZAR": {
                    "buy": float(latest_data["zar_buy"]),
                    "sell": float(latest_data["zar_sale"]),
                    "mid": float((latest_data["zar_buy"] + latest_data["zar_sale"]) / 2),
                },
            },
        }

        # Generate historical data (hybrid approach: daily for past year, monthly for older)
        historical_data = []

        # Calculate cutoff date (12 months ago from latest data)
        cutoff_date = latest_date - pd.DateOffset(months=12)
        logger.info(f"Using daily data from {cutoff_date.date()} onwards, monthly averages before")

        # Split data into recent (daily) and older (monthly) periods
        recent_data = df_sorted[df_sorted["date_only"] >= cutoff_date.date()].copy()
        older_data = df_sorted[df_sorted["date_only"] < cutoff_date.date()].copy()

        # Process older data as monthly averages
        monthly_count = 0
        if not older_data.empty:
            older_data["year_month"] = older_data["date"].dt.to_period("M")
            monthly_avg = (
                older_data.groupby("year_month")
                .agg(
                    {
                        "date_only": "last",  # Use last date of the month
                        "usd_buy": "mean",
                        "usd_sale": "mean",
                        "gbp_buy": "mean",
                        "gbp_sale": "mean",
                        "eur_buy": "mean",
                        "eur_sale": "mean",
                        "zar_buy": "mean",
                        "zar_sale": "mean",
                        "normalized": "first",  # Whether this period is normalized
                    }
                )
                .reset_index()
            )
            monthly_count = len(monthly_avg)

            for _, row in monthly_avg.iterrows():
                historical_data.append(
                    {
                        "date": row["date_only"].isoformat(),
                        "USD": round((row["usd_buy"] + row["usd_sale"]) / 2, 3),
                        "GBP": round((row["gbp_buy"] + row["gbp_sale"]) / 2, 3),
                        "EUR": round((row["eur_buy"] + row["eur_sale"]) / 2, 3),
                        "ZAR": round((row["zar_buy"] + row["zar_sale"]) / 2, 3),
                        "normalized": bool(row["normalized"]),
                        "period_type": "monthly",
                    }
                )

        # Process recent data as daily values
        if not recent_data.empty:
            for _, row in recent_data.iterrows():
                historical_data.append(
                    {
                        "date": row["date_only"].isoformat(),
                        "USD": round((row["usd_buy"] + row["usd_sale"]) / 2, 3),
                        "GBP": round((row["gbp_buy"] + row["gbp_sale"]) / 2, 3),
                        "EUR": round((row["eur_buy"] + row["eur_sale"]) / 2, 3),
                        "ZAR": round((row["zar_buy"] + row["zar_sale"]) / 2, 3),
                        "normalized": bool(row["normalized"]),
                        "period_type": "daily",
                    }
                )

        # Sort historical data by date
        historical_data.sort(key=lambda x: x["date"])

        logger.info(
            f"Generated {len(historical_data)} historical data points "
            f"({len(recent_data)} daily, {monthly_count} monthly)"
        )

        # Calculate trends (compare current with previous month)
        trends = {}
        if len(historical_data) >= 2:
            current = historical_data[-1]
            previous = historical_data[-2]

            for currency in self.currencies:
                current_rate = current[currency]
                previous_rate = previous[currency]
                change = current_rate - previous_rate
                change_percent = (change / previous_rate) * 100 if previous_rate != 0 else 0

                trends[currency] = {
                    "change": round(change, 3),
                    # Invert percentage: negative change (Kwacha stronger) = positive percentage
                    "change_percent": round(-change_percent, 2),
                    # Inverted logic: lower rate = stronger Kwacha = "up", higher rate = weaker Kwacha = "down"
                    "direction": "down" if change > 0 else "up" if change < 0 else "stable",
                }

        return {
            "last_updated": datetime.now().isoformat(),
            "current_rates": current_rates,
            "historical_data": historical_data,
            "trends": trends,
            "metadata": {
                "total_records": len(df),
                "historical_data_points": len(historical_data),
                "daily_data_points": len(recent_data),
                "monthly_data_points": monthly_count,
                "date_range": {
                    "from": df_sorted["date_only"].min().isoformat(),
                    "to": df_sorted["date_only"].max().isoformat(),
                },
                "daily_data_cutoff": cutoff_date.date().isoformat(),
                "currencies": self.currencies,
                "rebase_date": self.rebase_date.isoformat(),
                "data_strategy": "hybrid",
                "data_strategy_description": "Daily values for past 12 months, monthly averages for older data",
            },
        }

    def save_web_data(self, data: Dict):
        """Save data files for web consumption"""
        # Save current rates for homepage widget
        current_rates_file = self.web_data_dir / "fx_current.json"
        with open(current_rates_file, "w") as f:
            json.dump(
                {
                    "last_updated": data["last_updated"],
                    "current_rates": data["current_rates"],
                    "trends": data["trends"],
                },
                f,
                indent=2,
            )

        # Save complete data for FX page
        complete_data_file = self.web_data_dir / "fx_data.json"
        with open(complete_data_file, "w") as f:
            json.dump(data, f, indent=2)

        # Save historical data separately for performance
        historical_file = self.data_dir / f"fx_historical_{datetime.now().strftime('%Y%m%d')}.json"
        with open(historical_file, "w") as f:
            json.dump(data["historical_data"], f, indent=2)

        logger.info(f"Web data saved to {self.web_data_dir}")

    def process_and_save(self):
        """Main method to fetch, process, and save FX data"""
        try:
            # Fetch raw data
            excel_content = self.fetch_data()

            # Process data
            df = self.process_excel_data(excel_content)
            df = self.normalize_pre_rebase_data(df)

            # Generate web data
            web_data = self.generate_web_data(df)

            # Save for web consumption
            self.save_web_data(web_data)

            logger.info("FX data processing completed successfully")
            return web_data

        except Exception as e:
            logger.error(f"FX data processing failed: {e}")
            raise


def update_fx_data(data_dir: Optional[Path] = None) -> Dict:
    """Update FX data and return the processed data"""
    processor = FXDataProcessor(data_dir)
    return processor.process_and_save()
