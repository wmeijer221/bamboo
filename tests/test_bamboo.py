from dataclasses import dataclass
import time

from beartype.typing import Optional, Tuple
from beartype import beartype
import pandas as pd

# from tqdm import tqdm
# tqdm.pandas()

import random

from bamboo import BambooObject, bamboo_transform, validate


def test_thing():

    added_time_t = 0
    k = 10_000
    slow_process_t = added_time_t / k
    df = pd.DataFrame(
        data={
            "id": [i for i in range(k)],
            "name": [random.choice(["Steve", "Babette", "Rosemary"]) for _ in range(k)],
            "favorite_color": [random.choice(["Red", "Turquoise", "Sage"]) for _ in range(k)],
        }
    )
    print(df.head())

    val_delta_time = 1
    start_time = time.time()
    df_val = df

    @beartype
    @dataclass(kw_only=True)
    class Person(BambooObject):
        id: int
        name: str
        favorite_color: str

    validate(df_val, Person)

    @beartype
    @dataclass(kw_only=True)
    class PersonWithStringIDAndHobby(Person):
        id: str
        hobby: Optional[str]

    @bamboo_transform
    def val_id_transform(person: Person) -> PersonWithStringIDAndHobby:
        hobby = random.choice(["Hockey", "Sculpting", "Reading"])
        time.sleep(slow_process_t)
        output = PersonWithStringIDAndHobby(
            id=str(person.id), name=person.name, favorite_color=person.favorite_color, hobby=hobby
        )
        return output

    df_val = df_val.apply(val_id_transform, axis=1)

    @beartype
    @dataclass(kw_only=True)
    class PersonWithMergedColorAndHobby(PersonWithStringIDAndHobby):
        merged_color_and_hobby: Tuple[str, str]
        favorite_color: None = None
        hobby: None = None

    @bamboo_transform
    def val_hobby_transform(person: PersonWithStringIDAndHobby) -> PersonWithMergedColorAndHobby:
        new_person = PersonWithMergedColorAndHobby(
            id=person.id,
            name=person.name,
            merged_color_and_hobby=(person.favorite_color, person.hobby if person.hobby is not None else "No hobby"),
        )
        return new_person

    df_val = df_val.apply(val_hobby_transform, axis=1)

    # validate(df_val, PersonWithMergedColorAndHobby)
    print(df_val.head())

    end_time = time.time()
    val_delta_time = end_time - start_time
    print(f"With validation took {val_delta_time:.3f} seconds")

    start_time = time.time()
    df_noval = df

    def noval_id_transform(person: pd.Series) -> pd.Series:
        hobby = random.choice(["Hockey", "Sculpting", "Reading"])
        time.sleep(slow_process_t)
        new_row = pd.Series([str(person["id"]), hobby])
        return new_row

    df_noval[["id", "hobby"]] = df_noval.apply(noval_id_transform, axis=1)

    def noval_hobby_transform(person: pd.Series) -> pd.Series:
        merged_color_and_hobby = (person["favorite_color"], person["hobby"])
        new_person = pd.Series([merged_color_and_hobby])
        return new_person

    df_noval["merged_color_and_hobby"] = df_noval.apply(noval_hobby_transform, axis=1)
    df_noval = df_noval.drop(columns=["hobby", "favorite_color"])
    print(df_noval.head())

    end_time = time.time()
    noval_delta_time = end_time - start_time
    print(f"Without validation took {noval_delta_time:.3f} seconds ({val_delta_time / noval_delta_time:.2f}x slower).")


if __name__ == "__main__":
    test_thing()
