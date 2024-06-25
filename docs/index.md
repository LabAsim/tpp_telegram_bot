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
