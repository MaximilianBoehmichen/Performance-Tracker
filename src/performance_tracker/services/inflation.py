import warnings

import httpx
import numpy as np
import pandas as pd

from performance_tracker.utils.fill_df import fill_unit

START_YEAR = 2014


class InflationService:
    indicator = "FP.CPI.TOTL.ZG"
    base_url = "https://api.worldbank.org/v2"
    start_date = "2015-01-01"
    country_dict = {"DEU": "DE"}

    def get_inflation_rate(self, country_iso3: str) -> pd.DataFrame:
        if country_iso3 == "":
            return fill_unit("interpolated_inflation")

        with httpx.Client() as client:
            try:
                result = client.get(
                    self.base_url
                    + "/country/"
                    + self.country_dict.get(country_iso3, country_iso3)
                    + "/indicator/"
                    + self.indicator,
                    params={"format": "json", "per_page": 100},
                    timeout=20.0,
                )
            except httpx.ReadTimeout:
                warnings.warn("ReadTimeout for inflation API", stacklevel=2)

        result.raise_for_status()
        raw_inflation = result.json()[1]

        raw_df = pd.DataFrame(raw_inflation)
        raw_df["date"] = raw_df["date"].astype(int)
        raw_df["value"] = pd.to_numeric(raw_df["value"]) / 100

        raw_df = raw_df[raw_df["date"] > START_YEAR].sort_values("date")

        last_year = raw_df["date"].max()
        end_date = f"{last_year + 1}-01-01"
        daily_df = pd.DataFrame(
            index=pd.date_range(start=self.start_date, end=end_date, freq="D")
        )

        current_price_index = 1.0

        mapping = {"2015-01-01": current_price_index}
        for _, row in raw_df.iterrows():
            current_price_index *= 1 + row["value"]
            target_date = f"{row["date"] + 1}-01-01"
            mapping[target_date] = current_price_index

        daily_df["inflation"] = np.nan
        for date_str, val in mapping.items():
            if pd.Timestamp(date_str) in daily_df.index:
                daily_df.loc[date_str, "inflation"] = val

        daily_df["inflation_log"] = np.log(daily_df["inflation"])
        daily_df["inflation_log"] = daily_df["inflation_log"].interpolate(
            method="linear"
        )
        daily_df["interpolated_inflation"] = np.exp(daily_df["inflation_log"])

        return daily_df
