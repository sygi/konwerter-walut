#! /usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import datetime
import dateparser
import requests
import json
import readline  # only seemingly unused -- this changes flush behavior
from babel.dates import format_date

available_currencies =\
    ["USD", "AUD", "HKD", "CAD", "NZD", "SGD", "EUR", "HUF", "CHF", "GBP", "UAH",
     "JPY", "CZK", "DKK", "ISK", "NOK", "SEK", "HRK", "RON", "BGN", "RUB", "CNY"]


def get_rate(currency, date):
    """Reads the currency rate for a given day from the NBP page.

    Args:
        currency: 3-letter ISO code for the currency
        date: date in form of datetime date
    Returns:
        A pair: float, the average rate for the day or the last business day
        before and the date for which the rate was taken
    """
    status = 400
    while status is not 200:
        url = ("http://api.nbp.pl/api/exchangerates/rates/A/%s/%d-%02d-%02d?format=json" %
              (currency, date.year, date.month, date.day))

        response = requests.get(url)
        status = response.status_code
        date = date - datetime.timedelta(1)

    tree = json.loads(response.content)
    assert len(tree['rates']) == 1
    print_rate_info(tree['rates'])
    return (tree['rates'][0]['mid'], date)


def print_rate_info(rate):
    pass


def test_get_rate():
    assert get_rate("USD", datetime.date(2016, 9, 13))[0] == 3.8734


def test_non_business_day():
    rate, date = get_rate("USD", datetime.date(2016, 9, 11))
    assert rate == 3.8385
    assert date.day == 9


def test_other_currency():
    assert get_rate("CHF", datetime.date(2016, 9, 9))[0] == 3.9444


def main():
    income_pln = dict((cur, 0.) for cur in available_currencies)
    default_currency = "USD"
    while True:
        print("Suma przychodów: %f PLN." % sum(income_pln.values()))
        print("Podaj kolejną datę przychodu lub x aby zakończyć")
        date_str = raw_input()
        if date_str.lower() == 'x':
            break
        date = dateparser.parse(date_str)
        if date is None:
            print("Niezrozumiały format daty")
            continue
        print("Data przychodu:", format_date(date, locale="pl"))

        print("Podaj kwote przychodu razem z walutą (domyślna: %s) lub x"
              " aby poprawić datę" % default_currency)
        value_str = raw_input()
        if value_str.lower() == 'x':
            continue
        currency = ''.join(filter(str.isalpha, value_str))
        if currency == "":
            currency = default_currency
        else:
            if available_currencies.count(currency) == 0:
                print("Nieznana waluta:", currency)
                print("Oczekiwany format: https://pl.wikipedia.org/wiki/ISO_4217")
                continue
        default_currency = currency

        try:
            value = float(''.join(c for c in value_str if not str.isalpha(c)))
            rate, bill_date = get_rate(currency, date - datetime.timedelta(1))
        except Exception as e:
            print(e)
            continue

        print("Dodaje %d %s po kursie z %d.%d.%d (ostatni dzień roboczy przed)" %
              (value, currency, bill_date.day, bill_date.month,
                  bill_date.year))
        income_pln[currency] += rate * value
    print("Łączny przychód: %f PLN, w tym:" % sum(income_pln.values()))
    for cur, value in income_pln.iteritems():
        if abs(value) > 1e-3:
            print("%f in %s" % (value, cur))

if __name__ == "__main__":
    main()