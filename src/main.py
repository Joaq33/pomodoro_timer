import asyncio
import logging
import os
import sys
#import winsound
import playsound

import aioconsole

logger = logging.getLogger(__name__)
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(message)s", "%H:%M:%S")
)
logger.addHandler(logging_handler)
logger.setLevel(logging.INFO)


class Clock:
    lastline = ""
    count = 0
    printed_before = False
    bar_chars = ['█', "*", "#", "☼", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
                 "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    cleared = False
    reseted = False

    def __init__(self, timers, sound):
        if timers is None:
            timers = [13, 5]
        self.timers = timers
        self.sound = sound
        asyncio.run(self.lobby())

    async def lobby(self):
        """
        This is the lobby where you can set new timers and reset the counter
        :return:
        """
        self.prprint("Entered lobby", "debug")
        await self.room0()
        self.print_instructions()
        while True:
            full_result = await aioconsole.ainput()
            result = full_result.lower().split()
            if result[0] == "n":
                timers = get_valid_timers(result[1:])
                if timers:
                    self.timers = timers
                delete_last_line(7)
                if self.cleared:
                    delete_last_line()
                if self.reseted:
                    delete_last_line()
                timers_part = f"{'new timers ' if timers else ''}{self.timers}"
                join_part = f"{' and ' if self.reseted else ''}"
                reset_part = f'new counter: {self.count}' if self.reseted else ''
                self.prprint(f"n: {timers_part}{join_part}{reset_part}", "info")
                await self.room0()
                self.cleared = False
                self.reseted = False
                self.print_instructions()
            elif result[0] == "b":
                delete_last_line(6)
                self.del_if_cleared()
                self.prprint(f"{full_result}: closing", "info")
                break
            elif result[0] == "r":
                if len(result) == 2:
                    try:
                        self.count = int(result[1])
                        self.del_if_reseted()
                        self.prprint(f"r: setting counter to {result[1]}", "info")
                    except ValueError:
                        self.del_if_cleared()
                        self.prprint(f"r: invalid input: {result[1]}", "info")
                elif len(result) == 1:
                    self.del_if_reseted()
                    self.prprint("r: resetting counter", "info")
                    self.count = 0
                else:
                    self.prprint("r: invalid argument count input", "info")
            else:
                self.del_if_cleared()
                self.prprint(f"Input: {full_result}: invalid input", "info")

    def print_instructions(self):
        """
        Prints the instructions for the user
        :return:
        """
        self.prprint("-" * 20, "print")
        self.prprint("Back in lobby", "print")
        self.prprint("n - set new timers separated by spaces", "print")
        self.prprint("r - reset counter or set new counter separated by space", "print")
        self.prprint("b - escape program", "print")
        self.prprint("-" * 20, "print")

    def del_if_reseted(self):
        """
        Deletes the reseted message if it is printed
        :return:
        """
        if self.reseted:
            delete_last_line()
        else:
            self.reseted = True
        delete_last_line()
        if self.cleared:
            delete_last_line()
            self.cleared = False

    def del_if_cleared(self):
        """
        Deletes the cleared message if it is printed
        :return:
        """
        if self.cleared:
            delete_last_line()
        else:
            self.cleared = True
        delete_last_line()

    async def room0(self):
        """
        This is the timer room
        :return:
        """
        self.prprint("Entered room0", "debug")
        self.printed_before = False
        task1 = asyncio.ensure_future(self.time_tracker())
        task2 = asyncio.create_task(self.input_tracker())
        escapable = await task2
        if escapable:
            task1.cancel()
            self.prprint(f"b: escaped, [total count: {self.count}]", "info")

    def prprint(self, texto, mode="info"):
        """
        Prints the text in the correct mode
        :param texto:
        :param mode:
        :return:
        """
        if self.lastline:
            # Here should delete the last line, write the new one and rewrite the last line
            delete_last_line()
            print_level(texto, mode)
            print(self.lastline)
        else:
            # Here should print the new text
            print_level(texto, mode)

    async def time_tracker(self):
        """
        This is the timer task
        :return:
        """
        self.prprint("Entered time_tracker", "debug")
        while True:
            for timer_id in range(len(self.timers) - 1):
                await self.gen_lastline(timer_id)
            self.count += 1
            await self.gen_lastline(len(self.timers) - 1)

    async def gen_lastline(self, timer_id):
        """
        Generates the last line of the timer
        :param timer_id:
        :return:
        """
        timer = self.timers[timer_id]
        time_count = timer
        timer_char = self.bar_chars[timer_id]

        # To play audio in background, use playsound module if not in windows
        if self.sound:
            #winsound.PlaySound(None, winsound.SND_ASYNC)
            #winsound.PlaySound(f"{self.parentdir}/sounds/sound_{timer_id % 2 + 1}.wav",
                               # get sound count from folder
            #                   winsound.SND_ASYNC | winsound.SND_ALIAS)
            playsound.playsound(f"{self.parentdir}/sounds/sound_{timer_id % 2 + 1}.wav", False)

        while time_count > 0:
            self.lastline = f"[{genbar(1 - time_count / timer, timer_char)}]: {timer - time_count}/{timer} || Phase: {timer_id + 1}/{len(self.timers)} || Epoc: {self.count}"
            self.refresh_lastline()
            await asyncio.sleep(1)
            time_count -= 1

    def refresh_lastline(self):
        """
        Refreshes the last line of the timer
        :return:
        """
        if self.printed_before:
            delete_last_line()
        self.printed_before = True
        print(self.lastline)

    async def input_tracker(self):
        """
        This is the input task
        :return:
        """
        self.prprint("Entered input_tracker", "debug")
        ya_logeado = False
        while True:
            result = await aioconsole.ainput()
            if result == "b":
                delete_last_line(2)
                if ya_logeado:
                    delete_last_line()
                self.lastline = ""
                return True
            else:
                delete_last_line()
                if not ya_logeado:
                    ya_logeado = True
                else:
                    delete_last_line()
                self.prprint(f"Input: {result}", "info")


def delete_last_line(n=1):
    """
    Deletes the last n lines
    :param n:
    :return:
    """
    cursor_up_one = '\x1b[1A'
    erase_line = '\x1b[2K'
    for _ in range(n):
        print((cursor_up_one + erase_line) * 1, end="\r")


def genbar(n, char, length=20):
    """
    Generates a bar with the given length and char
    :param n:
    :param char:
    :param length:
    :return:
    """
    return char * int(n * length) + " " * (length - int(n * length))


def print_level(texto, mode):
    """
    Prints the text in the correct mode
    :param texto:
    :param mode:
    :return:
    """
    if mode == "info":
        logger.info(texto)
    if mode == "warning":
        logger.warning(texto)
    if mode == "error":
        logger.error(texto)
    if mode == "critical":
        logger.critical(texto)
    if mode == "debug":
        logger.debug(texto)
    if mode == "print":
        print(texto)


def get_valid_timers(args):
    """
    Gets the valid timers from the args
    :param args:
    :return:
    """
    timers = []
    # try each element to be an int
    try:
        if len(args) == 0:
            return None
        for arg in args:
            timers.append(int(arg))
        return timers
    except ValueError:
        logger.info("Invalid argument, must be an int, setting to default...")
        return None


if __name__ == '__main__':
    sound = True
    args = sys.argv[1:]
    newargs = []
    for arg in args[1:]:
        if arg == "--debug":
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode activated")
        elif arg == "--info":
            logger.setLevel(logging.INFO)
            logger.info("Info mode activated")
        elif arg == "--nosound":
            sound = False
        else:
            newargs.append(arg)
    timers = get_valid_timers(newargs)
    if not timers:
        timers = [13, 5]
    Clock(timers, sound)
