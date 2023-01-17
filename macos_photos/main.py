import osxphotos
from os.path import expanduser
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from datetime import datetime
from pipe import select, where

from collections import defaultdict

## visualizations
def chart_persons_pie(db):
    fig, ax = plt.subplots()
    persons = db.persons_as_dict
    del persons['_UNKNOWN_']
    sizes = persons.values()
    labels = persons.keys()
    ax.pie(sizes, labels=labels)

def chart_photos_by_time(ax, db):
    times = list(db.photos() | select(lambda p: p.date))
    start_date = datetime(2016, 1, 1)
    end_date = max(times)

    # auto format dates on x axis https://stackoverflow.com/a/39748305/10372825
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))


    ax.set_title("photos taken over time")
    ax.hist(times, range=(start_date, end_date), bins=100)
    return ax

def chart_days_with_people_bar(ax, db):
    metas = list(db.photos() | select(lambda p: (p.date, p.persons)))
    start_date = datetime(2016, 1, 1)
    end_date = max(metas)

    print(metas[0])

    # deduplicate dates
    dates_by_person = defaultdict(set)
    for time, persons in metas:
        date = time.date()
        for person in persons:
            dates_by_person[person].add(date)
    del dates_by_person['_UNKNOWN_']

    sizes = list(dates_by_person.values() | select(len))
    labels = dates_by_person.keys()

    sizes, labels = zip(* (zip(sizes, labels) | where(lambda p: p[0] > 5)))

    sizes, labels = zip(* sorted(zip(sizes, labels), key=lambda p: p[0], reverse=True))
    ax.bar(labels, sizes)
    # tilt the labels to not overlap https://stackoverflow.com/a/14854007/10372825
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_title("# of days where person appeared in photos")

    # ax.pie(sizes, labels=labels)

    return ax

## main
def main():
    db = osxphotos.PhotosDB(expanduser("~/Pictures/Photos Library.photoslibrary"))
    # chart_persons_pie(db)

    fig, ax = plt.subplots()
    # ax = chart_photos_by_time(ax, db)
    ax = chart_days_with_people_bar(ax, db)
    fig.tight_layout()
    plt.show()



if __name__ == '__main__':
    main()
