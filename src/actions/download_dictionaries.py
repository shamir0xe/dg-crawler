from tqdm import tqdm
from src.facades.cat_graph import CatGraph
from src.facades.cats import Cats
from src.helpers.config import Config
from src.orchestrators.send_request import SendRequest


class DownloadDictionaries:
    @staticmethod
    def dl() -> None:
        endpoint = Config.read("main.urls.dictionary")
        data = SendRequest.send(endpoint)
        if not data or "data" not in data:
            raise Exception("Cannot fetch dictionaries")
        for obj in tqdm(data["data"]):
            if "type" in obj:
                type_ = obj["type"].lower()
                if type_ == "category_tree" and "data" in obj:
                    CatGraph().build_graph(obj["data"])
                elif type_ == "categories" and "data" in obj:
                    Cats().load(obj["data"])
