import attr
from datetime import datetime
from uuid import uuid4
from io import BytesIO
import pandas as pd
from XCaliburMethodReader import load_lc_data, get_lc_gradient, get_lc_settings

@attr.s
class Sequence:
    filename: str = attr.ib()
    method_filename: str = attr.ib()
    date: datetime = attr.ib()
    lc_settings: pd.DataFrame = attr.ib()
    gradient: pd.DataFrame = attr.ib()
    comments: dict = attr.ib()
    samples: list = attr.ib()
    table: pd.DataFrame = attr.ib()
    batch_id: str = attr.ib(default=attr.Factory(lambda: str(uuid4())[:5].upper()))

    @classmethod
    def from_xcalibur_csv_and_method(cls, filename, csv_data, method_filename, method_data):
        """Returns Sequence from csv string data."""
        df = pd.read_csv(BytesIO(csv_data), skiprows=[0])
        date = datetime.now()

        lc_data = load_lc_data(BytesIO(method_data))
        lc_settings = get_lc_settings(lc_data)
        gradient = get_lc_gradient(lc_data)

        sequence = cls(
            filename=filename,
            method_filename=method_filename,
            date=date,
            lc_settings=lc_settings,
            gradient=gradient,
            comments=dict([el.strip() for el in item.split(':')] for item in df['Comment'][0].split(',')),
            samples=[row for _, row in df.iterrows()],
            table=df,
        )

        return sequence

    @property
    def run_time(self):
        df = self.table
        gradient = self.gradient
        dur = ((len(df[df['Sample Type'] != 'QC']) * (gradient['duration'].sum() / 60 + 30)) + (
                    len(df[df['Sample Type'] == 'QC']) * (15 + 30))) / 60.
        return dur

    @staticmethod
    def to_xcalibur_csv(df, bracket=4):
        """
        Returns an XCalibur-formatted csv as a string (with 'bracket' put in the header), given a pandas DataFrame.
        """
        return 'Bracket Type={}{}\n{}'.format(bracket, ',' * (df.shape[1] - 1), df.to_csv(index=False))

