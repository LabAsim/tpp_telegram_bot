import dataclasses
import re
import time
import unicodedata
from datetime import datetime, timedelta
from typing import Any, Union


@dataclasses.dataclass
class NewsDataclass:
    """
    A Dataclass containing the scraped info.
    """

    date: Any
    url: str = ""
    main_content: str = ""
    summary: str = ""
    title: str = ""
    author: str = ""
    author_url: str = ""
    date_unix: int = 0
    category: str = ""
    debug: bool = True

    def __post_init__(self):
        # Convert date to UNIX timestamp
        try:
            self.date_unix = NewsDataclass.date_to_unix(self.date)
        except (Exception, ValueError, IndexError):
            pass
        # Strip unnecessary characters
        try:
            self.main_content = self.strip_ansi_characters(self.main_content)
            self.summary = self.strip_ansi_characters(self.summary)
            self.author = self.strip_ansi_characters(self.author)
            self.author_url = self.strip_ansi_characters(self.author_url)
        except Exception:
            raise
        # Lower first letters
        self.category = self.category.lower()

    def __str__(self):
        return f'Name:"{self.url}"'

    def strip_ansi_characters(self, text=""):
        """
        https://stackoverflow.com/questions/48782529/exclude-ansi-escape-sequences-from-output-log-file
        https://www.tutorialspoint.com/How-can-I-remove-the-ANSI-escape-sequences-from-a-string-in-python
        """
        try:
            # ansi_re = re.compile(r'[^\x00-\x7F]+')
            # return re.sub(r'[^\x00-\x7F]+', ' ', text)
            """text = text.encode("ascii", "ignore")
            text = text.decode()
            print(text)
            return text"""
            #  γνωστό ότι\xa0τα ΜΜΕ\xa0θα ενημερώνοντ
            ansi_re = re.compile(r"\x1b\[[0-9;]*m")
            text = re.sub(ansi_re, " ", text)
            ansi_re = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
            ansi_re = re.compile("([\\\]x[\w\d]{,3})")
            text = re.sub(ansi_re, " ", text)
            # https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize
            # https://stackoverflow.com/a/34669482

            return text

        except re.error as err:
            print(err)

    @staticmethod
    def date_to_unix(_date: str) -> Union[int, float]:
        """
        Converts and returns the date to unix timestamp
        :param _date: Date in various forms
        :return: Unix timestamp
        See also:
            examples: https://www.devdungeon.com/content/working-dates-and-times-python-3
        Python docs:
            time: https://docs.python.org/3/library/time.html
            datetime: https://docs.python.org/3/library/datetime.html
        """

        # Make sure it's a string. Date is a tuple containing the date and an integer from sorting function (sortby())
        # date = str(date[0]).strip()
        # Note that date is an attribute of this Dataclass. Do not override it.
        _date = str(_date)
        # If the date is in the form of "Πριν 6 ώρες/λεπτά"
        if re.match("[Ππ]ρ[ιίΙ]ν", _date):
            # Remove 'Πριν/πριν'
            # See docs: https://docs.python.org/3/library/re.html#re.sub
            _date = re.sub(pattern="[Ππ]ρ[ιίΙ]ν", repl="", string=_date).lstrip(" ")
            if "δευ" in _date:  # "39 δευτερόλεπτα"
                date_now = datetime.now()
                _date = _date.split(" ")
                _date = float(_date[0].strip(" ́").strip())
                unix_date = date_now - timedelta(seconds=_date)
                unix_date = time.mktime(unix_date.timetuple())
                return unix_date
            elif "λεπτ" in _date:  # "2 λεπτά"
                date_now = datetime.now()
                _date = re.sub(
                    pattern="[Λλ]{,2}επτ[αΑάΆοοΟόΌ]{,1}",
                    repl="",
                    string=_date,
                    flags=re.IGNORECASE,
                ).lstrip(" ")
                _date = float(_date.strip(" ́").strip())
                unix_date = date_now - timedelta(minutes=_date)
                unix_date = time.mktime(unix_date.timetuple())
                return unix_date
            # elif re.search("[ωώ]ρ[εα][ς]?", date, flags=re.IGNORECASE):#"ώρ" in date: #  # "2 ώρες / ώρα" pass
            elif "ώρ" or "ωρ" or "ω΄ρ" in _date:
                date_now = datetime.now()
                _date = _date.split(" ")
                # date = re.sub(pattern="\s[ωώ]ρ[εα][ςΣ]?", repl="", string=date, flags=re.IGNORECASE).lstrip(' ')
                # date = date.strip('Πριν').strip("ώρα").strip("ώρες").strip()
                _date = float(_date[0].strip(" ́").strip())
                unix_date = date_now - timedelta(hours=_date)
                unix_date = time.mktime(unix_date.timetuple())
                return unix_date
            else:  # '1 ημέρα'
                date_now = datetime.now()
                _date = _date.split(" ")
                _date = float(_date[0])
                unix_date = date_now - timedelta(days=_date)
                unix_date = time.mktime(unix_date.timetuple())
                return unix_date
        # Date is in the form of "19/10/22"
        elif "/" in _date:
            _date = _date.split("/")
            year = int(_date[-1])
            month = int(_date[1])
            day = int(_date[0])
            unix_date = datetime(year, month, day)
            unix_date = time.mktime(unix_date.timetuple())
            return unix_date
        # The date is in the form of "Κυριακή 18 Δεκεμβρίου 2022"
        else:
            _date = _date.split()
            _date = _date[1:]  # Drop the name of the day
            year = int(_date[-1])
            month = NewsDataclass.month_str_to_int(_date[1])
            day = int(_date[0])
            unix_date = datetime(year, month, day)
            unix_date = time.mktime(unix_date.timetuple())
            # print(f"from a string: {unix_date}")
            return unix_date

    @staticmethod
    def month_str_to_int(month: str) -> int:
        """
        Converts a string based month to an integer based month. i.e. 'Δεκέμβρης' -> 12
        :param month: str
        :return: int
        """
        if re.match("Ιανου[αά]ρ[ιί][οuη]{,2}", month) or re.match("Γεν[αά]ρης", month):
            return 1
        elif re.match("Φεβρου[αά]ρ[ιί][οuη]{,2}", month) or re.match("Φλεβ[αά]ρης", month):
            return 2
        elif re.match("Μ[αά]ρτ[ιί][οuη]{,2}", month):
            return 3
        elif re.match("Απρ[ιί]λ[ιί][οuη]{,2}", month):
            return 4
        elif re.match("Μ[αά][ιί][οuη]{,2}", month):
            return 5
        elif re.match("Ιο[υύ]ν[ιί][οuη]{,2}", month):
            return 6
        elif re.match("Ιο[υύ][ιί][οuη]{,2}", month):
            return 7
        elif re.match("Α[υύ]γο[υύ]στου", month):
            return 8
        elif re.match("Σεπτ[εέ]μβρ[ιί][οuη]{,2}", month):
            return 9
        elif re.match("Οκτ[ωώ]βρ[ιί][οuη]{,2}", month):
            return 10
        elif re.match("Νο[εέ]μβρ[ιί][οuη]{,2}", month):
            return 11
        elif re.match("Δεκ[εέ]μβρ[ιί][οuη]{,2}", month):
            return 12

    @staticmethod
    def unix_to_datetime(unixtimestamp: int) -> str:
        """Converts unix timestampe to datetime format (DD/MM/YYYY)"""
        return datetime.utcfromtimestamp(unixtimestamp).strftime("%d/%m/%Y")

    def return_as_tuple(self):
        """
        Returns all attributes in a tuple.
        Alternative, just use dataclasses.astuple(object).
        See: https://docs.python.org/3/library/dataclasses.html#dataclasses.astuple
        """
        tuple_to_return = [
            self.date,
            self.url,
            self.main_content,
            self.summary,
            self.title,
            self.author,
            self.author_url,
            self.date_unix,
            self.category,
        ]
        for number, a in enumerate(tuple_to_return):
            if a not in (self.date_unix, None):
                tuple_to_return[number] = unicodedata.normalize("NFKD", a)
                tuple_to_return[number] = tuple_to_return[number].strip("'").strip('"')
        return tuple(tuple_to_return)
