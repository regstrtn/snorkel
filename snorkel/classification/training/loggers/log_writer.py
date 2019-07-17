import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Any, DefaultDict, List, Mapping

from snorkel.classification.snorkel_config import default_config
from snorkel.classification.utils import recursive_merge_dicts
from snorkel.types import Config


class LogWriter:
    """A class for writing logs.

    Parameters
    ----------
    kwargs
        Configuration merged with ``default_config["log_writer_config"]``

    Attributes
    ----------
    config
        Merged configuration
    run_name
        Name of run if provided, otherwise date-time combination
    log_dir
        Path root logging directory
    run_log
        Dictionary of scalar values to log, keyed by value name
    """

    def __init__(self, **kwargs: Any) -> None:
        assert isinstance(default_config["log_writer_config"], dict)
        self.config = recursive_merge_dicts(default_config["log_writer_config"], kwargs)

        date = datetime.now().strftime("%Y_%m_%d")
        time = datetime.now().strftime("%H_%M_%S")
        self.run_name = self.config["run_name"] or f"{date}/{time}/"

        self.log_dir = os.path.join(self.config["log_dir"], self.run_name)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.run_log: DefaultDict[str, List[List[float]]] = defaultdict(list)

    def add_scalar(self, name: str, value: float, step: float) -> None:
        """Log a scalar variable.

        Parameters
        ----------
        name
            Name of the scalar collection
        value
            Value of scalar
        step
            Step axis value
        """
        # Note: storing as list for JSON roundtripping
        self.run_log[name].append([step, value])

    def write_config(
        self, config: Config, config_filename: str = "config.json"
    ) -> None:
        """Dump the config to file.

        Parameters
        ----------
        config
            JSON-compatible config to write to TensorBoard
        config_filename
            Name of file in logging directory to write to
        """
        self.write_json(config, config_filename)

    def write_log(self, log_filename: str) -> None:
        """Dump the scalar value log to file.

        Parameters
        ----------
        log_filename
            Name of file in logging directory to write to
        """
        self.write_json(self.run_log, log_filename)

    def write_text(self, text: str, filename: str) -> None:
        """Dump user-provided text to filename (e.g., the launch command).

        Parameters
        ----------
        text
            Text to write
        filename
            Name of file in logging directory to write to
        """
        text_path = os.path.join(self.log_dir, filename)
        with open(text_path, "w") as f:
            f.write(text)

    def write_json(self, dict_to_write: Mapping[str, Any], filename: str) -> None:
        """Dump a JSON-compatbile object to root log directory.

        Parameters
        ----------
        dict_to_write
            JSON-compatbile object to log
        filename
            Name of file in logging directory to write to
        """
        if not filename.endswith(".json"):  # pragma: no cover
            logging.warning(
                f"Using write_json() method with a filename without a .json extension: {filename}"
            )
        log_path = os.path.join(self.log_dir, filename)
        with open(log_path, "w") as f:
            json.dump(dict_to_write, f)

    def close(self) -> None:
        """Close writer if necessary."""
        pass