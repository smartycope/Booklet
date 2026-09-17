AudiobookshelfLandingPage
    "Resume {current book title}" -> Player

    "Download a Book" -> SelectCloudBookPage(download=True)
    "Stream a Book" -> SelectCloudBookPage(download=False)
        "In Progress" -> SelectInProgressBookPage
        "Recently Added" -> SelectRecentlyAddedPage
            PlayerPage/DownloadBookPage

        "All Series/Books" -> SelectAllBooksPage
        "Select by Author" -> ChooseFromAuthorPage
        "Select by Genre" -> ChooseFromGenrePage
            # Go to the series page, if a series was selected, otherwise go straight to PlayerPage/DownloadBookPage
            ChooseFromSeries(series_id) -> PlayerPage/DownloadBookPage
            PlayerPage/DownloadBookPage

    "Play downloaded Book" -> SelectDownloadedBookPage(delete=False)
        PlayerPage

    "Deleted Downloaded Book" -> SelectDownloadedBookPage(delete=True)

# SelectDownloadedBookPage, DownloadBookPage, and PlayerPage don't go anywhere, other than back to their previous page
