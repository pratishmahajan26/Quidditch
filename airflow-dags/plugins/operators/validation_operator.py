from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import pandas as pd
import os


class DataValidationOperator(BaseOperator):
    @apply_defaults
    def __init__(self, input_file_path, *args, **kwargs):
        super(DataValidationOperator, self).__init__(*args, **kwargs)
        self.input_file_path = input_file_path

    def execute(self, context):
        try:
            if not os.path.exists(self.input_file_path):
                raise FileNotFoundError(f"Input file not found at {self.input_file_path}")

            df = pd.read_csv(self.input_file_path)
            if df.empty:
                raise ValueError("Input file is empty.")

            if 'sale_id' not in df.columns:
                raise ValueError("Required column missing in the input file.")

            self.log.info("Data validation successful.")

            return "success"
        except Exception as e:
            raise Exception(f"Data validation failed with exception: {e}")
