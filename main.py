from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window
import os 
import pandas as pd
import threading
import yfinance as yf

class StockApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        # Instead of fcntl.flock(file_descriptor, fcntl.LOCK_EX)
        
        # Input Area
        self.input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.text_input_symbol = TextInput(text='Enter symbol', multiline=False, font_size=12)
        self.text_input_start_date = TextInput(text='Enter start date (YYYY-MM-DD)', multiline=False, font_size=12)
        self.text_input_end_date = TextInput(text='Enter end date (YYYY-MM-DD)', multiline=False, font_size=12)
        self.fetch_button = Button(text='Get Stock Data', on_press=self.fetch_data, font_size=12)
        self.fetch_options_chain_button = Button(text='Get Options Chain', on_press=self.fetch_options_chain, font_size=12)

        self.input_layout.add_widget(self.text_input_symbol)
        self.input_layout.add_widget(self.text_input_start_date)
        self.input_layout.add_widget(self.text_input_end_date)
        self.input_layout.add_widget(self.fetch_button)
        self.input_layout.add_widget(self.fetch_options_chain_button)

        self.layout.add_widget(self.input_layout)

        # Stock Table Area
        self.stock_table_layout = GridLayout(cols=6, spacing=10, size_hint_y=None)
        self.stock_scroll_view = ScrollView(size=(Window.width, Window.height / 2))
        self.layout.add_widget(self.stock_scroll_view)
        self.stock_scroll_view.add_widget(self.stock_table_layout)

        # Options Chain Table Area
        self.options_chain_table_layout = GridLayout(cols=7, spacing=10, size_hint_y=None)
        self.options_chain_scroll_view = ScrollView(size=(Window.width, Window.height / 2))
        self.layout.add_widget(self.options_chain_scroll_view)
        self.options_chain_scroll_view.add_widget(self.options_chain_table_layout)

        return self.layout

    def fetch_data(self, instance):
        symbol = self.text_input_symbol.text
        start_date = self.text_input_start_date.text
        end_date = self.text_input_end_date.text
        threading.Thread(target=self.fetch_data_thread, args=(symbol, start_date, end_date)).start()

    def fetch_options_chain(self, instance):
        symbol = self.text_input_symbol.text
        threading.Thread(target=self.fetch_options_chain_thread, args=(symbol,)).start()

    def fetch_data_thread(self, symbol, start_date, end_date):
        yfinance_data = self.get_stock_data_yfinance(symbol, start_date, end_date)
        Clock.schedule_once(lambda dt: self.update_table(self.stock_table_layout, yfinance_data))

    def fetch_options_chain_thread(self, symbol):
        options_chain_data = self.get_options_chain_yfinance(symbol)
        Clock.schedule_once(lambda dt: self.update_options_chain_table(self.options_chain_table_layout, options_chain_data))

    def get_stock_data_yfinance(self, symbol, start_date, end_date):
        try:
            stock_data = yf.download(symbol, start=start_date, end=end_date)
            return stock_data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def get_options_chain_yfinance(self, symbol):
        try:
            stock = yf.Ticker(symbol)
            options_chain = stock.options
            options_data = pd.DataFrame()
            for expiry_date in options_chain:
                options_data = pd.concat([options_data, stock.option_chain(expiry_date).calls])
            return options_data
        except Exception as e:
            print(f"Error fetching options chain data: {e}")
            return None

    def update_table(self, table_layout, data):
        table_layout.clear_widgets()

        if data is not None:
            # Add headers
            for header in data.columns:
                table_layout.add_widget(Label(text=str(header), font_size=12, color=(1, 1, 1, 1)))

            # Add data
            for index, row in data.iterrows():
                for value in row:
                    table_layout.add_widget(Label(text=str(value), font_size=12, color=(1, 1, 1, 1)))

    def update_options_chain_table(self, table_layout, data):
        table_layout.clear_widgets()

        if data is not None:
            # Add headers
            headers = ['Contract Symbol', 'Last Trade Date', 'Strike', 'Last Price', 'Bid', 'Ask', 'Change']
            for header in headers:
                table_layout.add_widget(Label(text=str(header), font_size=12, color=(1, 1, 1, 1)))

            # Add data
            for index, row in data.iterrows():
                contract_info = [row['contractSymbol'], row['lastTradeDate'], row['strike'], row['lastPrice'], row['bid'], row['ask'], row['change']]
                for value in contract_info:
                    table_layout.add_widget(Label(text=str(value), font_size=12, color=(1, 1, 1, 1)))

# Run the app
if __name__ == '__main__':
    StockApp().run()

