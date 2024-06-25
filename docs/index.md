# Telegram Bot for ThePressProject (TPP) and other news sites

This bot allows you to get the news titles of the supported sites on Telegram.

It either gets the rss feed or scrapes the sites for news.

The primary motivation for creating it was to have news served at scheduled times.



## **Commands**

```title="First encounter""
/start
```

![start_gif](https://github.com/LabAsim/tpp_telegram_bot/blob/master/docs/media/start.gif?raw=true)


```title="Choose your preferred language: Either Greek or English"
/lang[uage]
```

<img alt="lang_gif" src="https://github.com/LabAsim/tpp_telegram_bot/blob/master/docs/media/language.gif?raw=true"/>

```title="Prints the help message"
/help
```


![help_gif](https://github.com/LabAsim/tpp_telegram_bot/blob/master/docs/media/help.gif?raw=true)



### For TPP

```title="Search on TPP based on a keyword"
/s[earch]
```

*Examples*

* `/search BIOME`
* `/s Ελλάδα`


![s_biome_gif](https://github.com/LabAsim/tpp_telegram_bot/blob/master/docs/media/s_biome.gif?raw=true)

```title="Get the latest news of a category"
/c[ategory]
```

**Supported categories**

* News[room]
* Gre[ece]
* Pol[itics]
* Eco[nomy]
* Inter[national]
* Repo[rtage]
* Ana[lysis]
* Cul[ture]
* Anas[kopisi]
* [tpp.]radio
* [tpp.]tv
* [Eng]lish
  * *Examples*
    * `/category Newsroom`
    * `/c Politics`
    * `/c news`


![c_news_gif](https://github.com/LabAsim/tpp_telegram_bot/blob/master/docs/media/c_news.gif?raw=true)


### RSS-feed based functions

Just add a slash `/` in front of the supported news sites to get the latest news.
Of course, there are short versions, there is no need to type the full name.
Only lowercase names are allowed.

The functions are ***case-sensitive***.

Supported sites

* [Efsyn](https://www.efsyn.gr/) - `/efsyn`
* [Kathimerini english version](https://www.ekathimerini.com/) - `/kat`
* [To Vima](https://www.tovima.gr/) - `/tov`
* [Ert](https://www.ert.gr/) - `/ert`
* [Naftemporiki](https://www.naftemporiki.gr/) - `/naf`
* [Documento](https://www.documentonews.gr/) - `/doc`
* [Prin](https://prin.gr/) - `/prin`
* [Reporters United](https://www.reportersunited.gr/) - `/ru`
* [Kontra - eksegersi.gr](https://eksegersi.gr/) - `/kontra`
* [Guardian](https://www.theguardian.com/)
    * Guardian Europe - `/geu`
    * Guardian Middle East - `gme`
    * Guardian World - `/gw`
* [Reuters](https://www.reuters.com/) - `/reu`
    * Reuters International - `/rint`
    * Reuters Politics - `/rpol`
    * Reuters News - `/rnews`
* [BBC](https://www.bbc.com/)
    * BBC World - `/bbcw`
    * BBC Top stories International - `/bbctpint`
    * BBC Europe - `/bbceu`
    * BBC Science - `/bbcsc`
* [CNN](https://edition.cnn.com/) - `/cnn`
    * CNN world - `/cnnw`
    * CNN Europe - `/cnneu`
* [DW](https://www.dw.com/en) - `/dw`
    * DW World - `/dweu`
    * DW Science - `/dwsc`
    * DW Asia - `/dwasia`
    * DW Enviroment - `/dwenv`


![kontra_gif](https://github.com/LabAsim/tpp_telegram_bot/blob/master/docs/media/kontra.gif?raw=true)


### Scheduling

You can schedule your news delivery.


```title="Schedule RSS based functions"
/sch[edule] <news command> <interval>
```

* `Interval` should be either an **integer** representing days *or* a **string** indicating the names of the days
  * Valid **integer** days: `1 to infinity`
  * Valid **string** days: `mon, tue, wed, thu, fri, sat, sun`
  * Examples:
    * `/sch ert 1`
    * `/sch ert mon-fri`


```title="Schedule search"
/sch[edule] search <search term> <interval>
```

* `search term` is any term that you want to get news for
* `Interval` should be either an **integer** representing days *or* a **string** indicating the names of the days
  * Valid **integer** days: `1 to infinity`
  * Valid **string** days: `mon, tue, wed, thu, fri, sat, sun`
  * Examples:
    * `/sch search ΒΙΟΜΕ ert mon-fri`
    * `/sch search ΒΙΟΜΕ ert 1`

```title="Schedule category news"
/sch[edule] category <category> <interval>
```

* `category` is a valid category of `/category`.
* `Interval` should be either an **integer** representing days *or* a **string** indicating the names of the days
  * Valid **integer** days: `1 to infinity`
  * Valid **string** days: `mon, tue, wed, thu, fri, sat, sun`
  * Examples:
    * `/sch category news ert 1`
    * `/sch category news ert mon-fri`

```title="Fetch all your active schedules"
/mysch[edule]
```

The bot sends you back your schedules

```title="Deletes a particular schedule"
/del[ete]
```

This function works **only** *if you reply at a message which contains a particular schedule from `/mysch`*.

```title="Deletes all your schedules"
/del[ete]all
```

Erases every saved schedule that you had.

```title="Deletes all your saved info including your schedules"
/deleteme
```

This functions deletes all your saved info including your schedules.
If you reply to the bot anytime after invoking `/deleteme`,
it will save again your telegram name and user id.
