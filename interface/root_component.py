import tkinter as tk
from tkinter.messagebox import askquestion
import logging
import time

from interface.styling import *
from interface.screener_component import Screener
from clientTweepy.tw import Tweets


logger = logging.getLogger()  # This will be the same logger object as the one configured in main.py


class Root(tk.Tk):
    def __init__(self, tw: Tweets):
        super().__init__()

        self.tw = tw


        self.title("Tweet Scalp")
        self.protocol("WM_DELETE_WINDOW", self._ask_before_close)

        self.configure(bg=BG_COLOR, width=2000)

        # Creates and places components at the top and bottom of the left and right frame

        self._screener_frame = Screener(self, bg=BG_COLOR)
        self._screener_frame.pack(side=tk.TOP, padx=0)



        self._update_ui()  # Starts the infinite interface update loop




    def _ask_before_close(self):

        """
        Triggered when the user click on the Close button of the interface.
        This lets you have control over what's happening just before closing the interface.
        :return:
        """

        result = askquestion("Confirmation", "Do you really want to exit the application?")
        if result == "yes":
            self.destroy()  # Destroys the UI and terminates the program


    def _update_ui(self):

        """
        Called by itself every 500 milliseconds. It is similar to an infinite loop but runs within the same Thread
        as .mainloop() thanks to the .after() method, thus it is "thread-safe" to update elements of the interface
        in this method. Do not update Tkinter elements from another Thread like a websocket thread.
        :return:
        """

        tree = self._screener_frame.tree

        try:
            for user, id in self.tw.accounts.items():


                if self.tw.tweets_data is not None:
                    self.tw.getTweets(id, user)
                    logger.warning('Getting tweets for %s', user)


                data = self.tw.tweets_data


                if user not in self.tw.full_data:
                    self.tw.full_data.append(user)
                    logger.warning("Recieved full data for %s users", len(self.tw.full_data))

                if data['tweet']:
                    twt = data['tweet']
                    data['tweet'] = self.tw.cleanTwt(twt)
                    logger.warning('Cleaning and Analising Tweets Tweets')


                if len(data['tweet']) == 0:
                    logger.warning('Tweet from %s discriminated because contains only this hyperlink', user)
                    continue


                if user not in self._screener_frame.user:
                    row_data = ["?", data['tweet'], "?", "?"]
                    tree.insert("", tk.END, user, text=user, values=row_data)
                    self._screener_frame.user.append(user)


                if data['tweet'] is not None:
                    twt = data['tweet']
                    logger.warning('Analising Tweets Tweets')
                    s = round(self.tw.getSubj(twt), 3)
                    p = round(self.tw.getPol(twt), 3)
                    data['sub'] = str(s)
                    data['pol'] = str(p)
                    data['sentiment'] = self.tw.getSent(float(data['pol']))
                    data['objectivity'] = self.tw.getSent2(float(data['sub']))

                tree.set(user, column='tweeted', value=str(data['tweeted']))
                tree.set(user, column="sentiment", value=data['sentiment'])
                tree.set(user, column="objectivity", value=data['objectivity'])


        # except RuntimeError:
        #     pass
        except Exception as e:
            print(e)

        if tree.last_sort is not None and time.time() - 1 > tree.last_auto_sort:
            tree.sort_column(*tree.last_sort)  # Keep the last sorting
            tree.last_auto_sort = time.time()  # Avoid sorting too often
        self.after(900000, self._update_ui)



