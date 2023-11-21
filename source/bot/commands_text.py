"""This module contains All the text messages"""
from aiogram import md


class Text:
    """Contains the text to be displayed for the bot commands"""

    save_lang_text_eng = "Language preference is saved 👍"
    save_lang_text_greek = "Η επιλογή γλώσσας αποθηκεύτηκε 👍"
    choose_lang_text = md.escape_md(
        "👋 Hello! Please select your language." "\n👋 Γεια! Διάλεξε τη γλώσσα επιλογής σου"
    )
    help_text_eng = md.text(
        md.bold("\n👇 -- The command list -- 👇\n"),
        "\n• /search or /s ",
        md.escape_md("\n\n\t\t\tArticle search based on a keyword"),
        "\n\n\t\t\tExample:\t/search ΒΙΟΜΕ",
        "\n",
        "\n• /category or /c  ",
        md.escape_md("\n\n\t\t\tSearch the latest news of the category"),
        md.escape_md("\n\n\t\t\tExample:\t/category Newsroom"),
        md.escape_md("\n\t\t\tExample:\t/category news"),
        md.escape_md("\n\n\t\t\tValid categories:"),
        md.escape_md("\n\t\t\t\t\t\tNews[room]"),
        md.escape_md("\n\t\t\t\t\t\tGre[ece]"),
        md.escape_md("\n\t\t\t\t\t\tPol[itics]"),
        md.escape_md("\n\t\t\t\t\t\tEco[nomy]"),
        md.escape_md("\n\t\t\t\t\t\tInter[national]"),
        md.escape_md("\n\t\t\t\t\t\tRepo[rtage]"),
        md.escape_md("\n\t\t\t\t\t\tAna[lysis]"),
        md.escape_md("\n\t\t\t\t\t\tCul[ture]"),
        md.escape_md("\n\t\t\t\t\t\tAnas[kopisi]"),
        md.escape_md("\n\t\t\t\t\t\t[tpp.]radio"),
        md.escape_md("\n\t\t\t\t\t\t[tpp.]tv"),
        md.escape_md("\n"),
        "\n• /language or /lang",
        md.escape_md("\n\n\t\t\tChoose your preferred language"),
        md.escape_md("\n\n• /help : Prints this help text"),
        "\n",
    )
    help_text_eng2 = md.text(
        md.bold("\n👇 -- The newspaper list -- 👇\n"),
        md.escape_md("\n• /efsyn"),
        "\nEfsyn",
        "\n",
        md.escape_md("\n• /kat"),
        "\nKathimerini english version",
        "\n",
        md.escape_md("\n• /tov"),
        "\nTo vima",
        "\n",
        md.escape_md("\n• /ert"),
        "\nErt",
        "\n",
        md.escape_md("\n• /naf"),
        "\nNaftemporiki",
        "\n",
        md.escape_md("\n• /doc"),
        "\nDocumento",
        "\n",
        md.escape_md("\n• /prin"),
        "\nPrin",
        "\n",
        md.escape_md("\n• /kontra"),
        md.escape_md("\nKontra - eksegersi.gr"),
        "\n",
    )
    help_text_greek = md.text(
        md.bold("\n👇 -- Η λίστα με όλες τις εντολές -- 👇\n"),
        "\n• /search ή /s ",
        md.escape_md("\n\n\t\t\tΑναζήτηση άρθρων βάσει λέξης κλειδί."),
        "\n\n\t\t\tΠαράδειγμα:\t/search ΒΙΟΜΕ",
        "\n",
        "\n• /category ή /c  ",
        md.escape_md("\n\n\t\t\tΑναζήτηση τελευταίων άρθρων συγκεκριμένης κατηγορίας."),
        md.escape_md("\n\n\t\t\tΠαράδειγμα:\t/category Newsroom"),
        md.escape_md("\n\n\t\t\tΚατηγορίες:"),
        md.escape_md("\n\t\t\t\t\t\tNews[room]"),
        md.escape_md("\n\t\t\t\t\t\tGre[ece]"),
        md.escape_md("\n\t\t\t\t\t\tPol[itics]"),
        md.escape_md("\n\t\t\t\t\t\tEco[nomy]"),
        md.escape_md("\n\t\t\t\t\t\tInter[national]"),
        md.escape_md("\n\t\t\t\t\t\tRepo[rtage]"),
        md.escape_md("\n\t\t\t\t\t\tA[nalysis]"),
        md.escape_md("\n\t\t\t\t\t\tCul[ture]"),
        md.escape_md("\n\t\t\t\t\t\tAnas[kopisi]"),
        md.escape_md("\n\t\t\t\t\t\t[tpp.]radio"),
        md.escape_md("\n\t\t\t\t\t\t[tpp.]tv"),
        md.escape_md("\n"),
        "\n• /language ή /lang",
        md.escape_md("\n\n\t\t\tΔιάλεξε τη γλώσσα της επιλογής σου"),
        md.escape_md("\n\n• /help : Τυπώνει αυτό το βοηθητικό κείμενο"),
        "\n",
    )
    help_text_greek2 = md.text(
        md.bold("\n👇 -- Η λίστα των εφημερίδων -- 👇\n"),
        md.escape_md("\n• /efsyn"),
        md.escape_md("\nΕφημερίδα των Συντακτών (Εφσυν)"),
        "\n",
        md.escape_md("\n• /kat"),
        md.escape_md("\nΚαθημερινή - αγγλική έκδοση"),
        "\n",
        md.escape_md("\n• /tov"),
        "\nΤο Βήμα",
        "\n",
        md.escape_md("\n• /ert"),
        "\nΕρτ",
        "\n",
        md.escape_md("\n• /naf"),
        "\nΝαυτεμπορική",
        "\n",
        md.escape_md("\n• /doc"),
        "\nDocumento",
        "\n",
        md.escape_md("\n• /prin"),
        "\nΠριν",
        "\n",
        md.escape_md("\n• /kontra"),
        md.escape_md("\nΚόντρα - eksegersi.gr"),
        "\n",
    )
    to_search_next_page_eng = "Do you want to search the next page?"
    to_search_next_page_greek = "Θέλετε να συνεχίσετε την αναζήτηση στην επόμενη σελίδα;"
    search_next_page_empty_keyword_page_no_1_eng = md.escape_md(
        "Nothing to search." "\nRepeat the search command /search <keyword>"
    )
    search_next_page_empty_keyword_page_no_1_greek = md.escape_md(
        "\nΕπαναλάβετε την αναζήτηση με την εντολή /search " "<λέξη κλειδί>"
    )
