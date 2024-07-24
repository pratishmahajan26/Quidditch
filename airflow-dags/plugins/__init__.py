from airflow.plugins_manager import AirflowPlugin
from operators.validation_operator import DataValidationOperator


class CustomPlugins(AirflowPlugin):
    name = "validation_operator_plugin"
    operators = [DataValidationOperator]
