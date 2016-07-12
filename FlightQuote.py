import datetime

class FlightQuote:
    def __init__(self, dp, rp, dt, rt, src):
        self.query_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M').encode("utf-8")
        self.dp = dp.encode("utf-8")
        self.rp = rp.encode("utf-8")
        self.dt = dt.encode("utf-8")
        self.rt = rt.encode("utf-8")
        self.src = src.encode("utf-8")
        self.agent = ''
        self.price = 0
        self.out_fights = []
        self.out_duration = 0
        self.in_flights = []
        self.in_duration = 0

    def add_quote(self, agent, px, o_flights, o_duration, i_flights=[], i_duration=0):
        self.agent = agent.encode("utf-8")
        self.price = px.encode("utf-8")
        self.out_fights = [x.encode('utf-8') for x in o_flights]
        self.out_duration = o_duration.encode("utf-8")
        self.in_flights = [x.encode('utf-8') for x in i_flights]
        self.in_duration = i_duration.encode("utf-8")

    def add_price(self, price):
        self.price = price

    def add_agent(self, agent):
        self.agent = agent.encode("utf-8")

    def add_out(self, out_flights, out_duration):
        self.out_flights = out_flights
        self.out_duration = out_duration

    def add_in(self, in_flights, in_duration):
        self.in_flights = in_flights
        self.in_duration = in_duration

    def format_info(self):
        formatted = [self.query_time, self.dp, self.rp, self.dt, self.rt, self.src]
        formatted.append(self.agent)
        formatted.append(str(self.price))
        formatted.append('|'.join(self.out_flights))
        formatted.append(str(self.out_duration))
        formatted.append('|'.join(self.in_flights))
        formatted.append(str(self.in_duration))
        return formatted

    def print_detail(self):
        to_print = self.format_info()
        print '\t'.join(to_print)
