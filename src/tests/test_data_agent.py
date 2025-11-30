import pytest
import pandas as pd
from src.agents.data_agent import DataAgent


def test_data_agent_loads_basic_csv(tmp_path):
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("date,impressions,clicks,spend,revenue,creative_message\n"
                        "2024-01-01,1000,10,20,50,ad1\n"
                        "2024-01-02,2000,20,40,100,ad2")

    agent = DataAgent(csv_path=str(csv_path))
    agent.load_data()

    assert isinstance(agent.df, pd.DataFrame)
    assert len(agent.df) == 2
    assert "impressions" in agent.df.columns


def test_data_agent_handles_missing_columns(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("wrongcol1,wrongcol2\n1,2")

    agent = DataAgent(csv_path=str(csv_path))

    with pytest.raises(ValueError):
        agent.load_data()


def test_data_agent_handles_empty_file(tmp_path):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("")

    agent = DataAgent(csv_path=str(csv_path))
    with pytest.raises(Exception):
        agent.load_data()


def test_data_agent_invalid_path():
    agent = DataAgent(csv_path="nonexistent.csv")
    with pytest.raises(FileNotFoundError):
        agent.load_data()
