# -*- coding: utf-8 -*-
"""
Get Tickets
"""
import datetime
import re
from utils import SBreak, MBreak, LBreak, Timer
from utils import PageError, TimeError
from utils import ParseHourMinute
from base import Base


class Booker(Base):
    URL = 'https://cupertino.apm.activecommunities.com/'
    COURT_PRIORITIES = [
        3, 4, 5, 10, 11, 12, 2, 9, 14, 15, 16, 17, 18, 8, 1, 7, 6]
    
    @classmethod
    def Copy(cls, other):
        cp = cls(other.b, other.multi_window, other.alerter)
        return cp
    
    def __init__(
            self,
            browser=None,
            multi_window=False,
            alerter='gmail'):
        super(Booker, self).__init__(
            browser, multi_window, alerter)
        self.url = 'https://cupertino.apm.activecommunities.com/'
        self.timer_a = Timer(20)
        self.timer_5 = Timer(5, logging=False)
        self.timer_5m = Timer(5*60)
        self.timer_hour = Timer(60*60)
        self.priority_map = self.MakeCourtPriorityMap()
        
    def MakeCourtPriorityMap(self):
        pmap = {}
        for pidx, court in enumerate(self.COURT_PRIORITIES):
            pmap[court] = pidx
        return pmap
        
    def Prepare(self):
        self.b.visit(self.url)
        self.ClickByXpath(
            '//div[@id=\'an-toolbar-links\']/a[contains(text(), \'Sign In\')]')        
    
    def IsSignedIn(self):
        if self.b.is_element_present_by_xpath(
                '//a[contains(text(), \'Sign In\')]', wait_time=5):
            return False
        if self.b.is_element_present_by_xpath(
                '//a[contains(text(), \'Sign Out\')]'):
            print('Signed In!')
            return True
        return False
        
    def SignIn(self, user='', pwd=''):
        self.TypeByXpath(
            '//input[contains(@id, \'UserName\')]',
            user)
        SBreak()
        self.TypeByXpath(
            '//input[contains(@id, \'Password\')]',
            pwd)

    def BlockBooking(self, block_until):
        tnow = datetime.datetime.now()
        last_refresh_time = tnow
        last_click_home = True
        while tnow < block_until:
            tnow = datetime.datetime.now()
            if tnow - last_refresh_time > datetime.timedelta(minutes=3):
                if last_click_home:
                    print('Refresh to reservation page')
                    self.ClickByXpath('//div[@id=\'an-nav\']//a[text()=\'Reservations\']')
                else:
                    print('Refresh to home page')
                    self.ClickByXpath('//div[@id=\'an-nav\']//a[text()=\'Home\']')
                last_click_home = not last_click_home
                last_refresh_time = tnow
            self.timer_5.Wait()
            
        
    def ReserveSearch(self, day, start_time='1pm', end_time='11pm'):
        self.b.visit(
            'https://apm.activecommunities.com/cupertino/ActiveNet_Home?'
            'FileName=onlinequickfacilityreserve.sdi')
        MBreak()
        element = self.b.find_by_xpath('//select[@id=\'facilitygroup_id\']')
        element.first.select('1')
        MBreak()
        year_element = self.b.find_by_id('begy')
        year_element.select(str(day.year))
        month_element = self.b.find_by_id('begm')
        month_element.select(str(day.month-1))
        day_element = self.b.find_by_id('begd')
        day_element.select(str(day.day))
        start_time = ParseHourMinute(start_time)
        self.TypeByXpath('//input[@id=\'begtime\']', start_time.strftime('%I'))
        start_ampm = start_time.strftime('%p').lower()
        self.ClickByXpath(
            f'//input[@name=\'ampmbegtime\'][@value=\'{start_ampm}\']')
        end_time = ParseHourMinute(end_time)
        self.TypeByXpath('//input[@id=\'endtime\']', end_time.strftime('%I'))
        end_ampm = end_time.strftime('%p').lower()
        self.ClickByXpath(
            f'//input[@name=\'ampmendtime\'][@value=\'{end_ampm}\']')
        SBreak()
        self.ClickByXpath(
            '//input[@type=\'submit\'][@value=\'Check Availability\']')
        
    def GetAvailableSlots(self, start_time='6pm', end_time='11:59pm', block_slots=''):
        block_slots_set = set()
        for block_slot in block_slots.split(','):
            block_court, block_time_str = block_slot.split(' ')
            block_court = int(block_court)
            block_time = ParseHourMinute(block_time_str)
            block_slots_set.add((block_court, block_time))
        tbs = self.b.find_by_xpath('//table[@class=\'tableListNoSort\']//table')
        start_time = ParseHourMinute(start_time)
        end_time = ParseHourMinute(end_time)
        res = []
        for tb in tbs:
            rows = tb.find_by_tag('tr')
            col_names = []
            for ridx, row in enumerate(rows):
                if ridx == 0:
                    col_names = [c.value for c in row.find_by_tag('th')]
                    continue
                cols = row.find_by_tag('td')
                row_dict = {}
                row_available = False
                court_priority = 0
                for cidx, col in enumerate(cols):
                    col_name = col_names[cidx]
                    if col_name == 'Name':
                        court_name = col.find_by_tag('a').text
                        court_idx = int(re.match(
                            r'.* (\d+) Tennis Court', court_name).group(1))
                        court_priority = self.priority_map[court_idx]
                        row_dict[col_name] = court_idx
                        continue
                    try:
                        res_time = ParseHourMinute(col_name)
                    except TimeError:
                        continue
                    if res_time < start_time or res_time > end_time:
                        continue
                    if (court_idx, res_time) in block_slots_set:
                        continue
                    if len(col.find_by_tag('img', 0.1)):
                        continue
                    checkbox = col.find_by_tag('input').first
                    if checkbox['disabled'] == 'true':
                        continue
                    row_dict[res_time.strftime('%H:%M')] = col
                    row_available = True
                if row_available:
                    res.append((court_priority, row_dict))
        return sorted(res)
    
    def Book(self, book_date, available_slots, reserve):
        if not available_slots:
            raise PageError('Cannot find available slots!')
        chosen_slot = available_slots[0][1]
        available_times = sorted([k for k in chosen_slot.keys() if k != 'Name'])
        if not available_times:
            raise PageError('Cannot find available time!')
        chosen_time = available_times[0]
        chosen_slot[chosen_time].find_by_tag('input').click()
        # Make click reserve button
        if reserve:
            self.ClickByXpath('//input[@name=\'reserve\']')
            LBreak()
        book_message = 'date {} at {}, on court {}.'.format(
            book_date.isoformat(), chosen_time, chosen_slot['Name'])
        return book_message
            
        
    def Run(self,
            book_date = None,
            book_start_time = '6pm',
            book_end_time = '11pm',
            block_booking_until = None,
            do_login = True,
            do_reserve = False,
            block_slots = ''):
        if book_date is None:
            dt_now = datetime.datetime.now()
            if dt_now.time() > datetime.time(8):
                book_date = dt_now + datetime.timedelta(days=8)
            else:
                book_date = dt_now + datetime.timedelta(days=7)
        else:
            book_date = datetime.datetime.strptime(book_date, '%Y-%m-%d')
            
        if block_booking_until is None:
            block_day = book_date - datetime.timedelta(days=7)
            block_booking_until = datetime.datetime(
                block_day.year, block_day.month, block_day.day, 8)
        else:
            block_booking_until = datetime.datetime.strptime(
                block_booking_until, '%Y-%m-%d %H:%M')
            
        book_date = book_date.date()
        print(
            'Try booking for {}, from {} to {}. Block booking until {}'.format(
                book_date.strftime('%F'), book_start_time, book_end_time,
                block_booking_until.isoformat()))
        
        if do_login:
            self.Prepare()
            MBreak()
            self.SignIn()
            while not self.IsSignedIn():
                self.timer_a.Wait()
                
        # Block booking, but refresh pages.
        self.BlockBooking(block_booking_until)
        available_slots = []
        while not available_slots:
            self.ReserveSearch(book_date)
            LBreak()
            print("Done search")
            available_slots = self.GetAvailableSlots(
                book_start_time, book_end_time, block_slots)
            if available_slots:
                break
            self.timer_5m.Wait()
        book_message = self.Book(book_date, available_slots, do_reserve)
        msg = f'Successful booked for {book_message}'
        self.SendAlert('Booked court', msg)
        
            

if __name__ == '__main__':
    booker = Booker(multi_window=False)
    # booker.Run('2021-07-15', '6pm', '7pm')
