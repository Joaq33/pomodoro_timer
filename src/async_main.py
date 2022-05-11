import asyncio
import logging
import os
import sys
import winsound

import aioconsole

logger = logging.getLogger(__name__)
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(message)s", "%H:%M:%S")
)
logger.addHandler(logging_handler)
logger.setLevel(logging.INFO)


def borrar_ultima_linea(n=1):
    cursor_up_one = '\x1b[1A'
    erase_line = '\x1b[2K'
    for _ in range(n):
        print((cursor_up_one + erase_line) * 1, end="\r")


def genbar(n, char, length=20):
    return char * int(n * length) + " " * (length - int(n * length))


def print_level(texto, mode):
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


class Clock:
    lastline = ""
    count = 0
    printed_before = False
    timer_chars = ['█', "*", "#", "☼", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
                   "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    parentdir = os.path.dirname(os.getcwd())
    cleared = False
    reseted = False

    def __init__(self, timers):
        if timers is None:
            timers = [13, 5]
        self.timers = timers
        asyncio.run(self.lobby())

    async def lobby(self):
        self.prprint("entered lobby", "debug")
        await self.room0()
        self.print_instructions()
        while True:
            full_result = await aioconsole.ainput()
            result = full_result.lower().split()
            if result[0] == "n":
                timers = get_valid_timers(result[1:])
                if timers:
                    self.timers = timers
                borrar_ultima_linea(7)
                if self.cleared:
                    borrar_ultima_linea()
                if self.reseted:
                    borrar_ultima_linea()
                timers_part = f"{'new timers ' if timers else ''}{self.timers}"
                join_part = f"{' and ' if self.reseted else ''}"
                reset_part = f'new counter: {self.count}' if self.reseted else ''
                self.prprint(f"n: {timers_part}{join_part}{reset_part}", "info")
                await self.room0()
                self.cleared = False
                self.reseted = False
                self.print_instructions()
            elif result[0] == "b":
                borrar_ultima_linea(7)
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
                        # borrar_ultima_linea()
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
                self.prprint(f"input: {full_result}: invalid input", "info")

    def print_instructions(self):
        self.prprint("-" * 20, "print")
        self.prprint("back in lobby", "print")
        self.prprint("n - set new timers separated by spaces", "print")
        self.prprint("r - reset counter or set new counter separated by space", "print")
        self.prprint("b - escape program", "print")
        self.prprint("-" * 20, "print")

    def del_if_reseted(self):
        if self.reseted:
            borrar_ultima_linea()
        else:
            self.reseted = True
        borrar_ultima_linea()
        if self.cleared:
            borrar_ultima_linea()
            self.cleared = False

    def del_if_cleared(self):
        if self.cleared:
            borrar_ultima_linea()
        else:
            self.cleared = True
        borrar_ultima_linea()

    async def room0(self):
        self.prprint("entered room0", "debug")
        self.printed_before = False
        task1 = asyncio.ensure_future(self.time_tracker())
        task2 = asyncio.create_task(self.input_tracker())
        escapable = await task2
        if escapable:
            task1.cancel()
            # borrar_ultima_linea()
            self.prprint(f"b: escaped, [total count: {self.count}]", "info")

    def prprint(self, texto, mode="info"):
        if self.lastline:
            # aca deberia borrar la ultima linea, escribir el nuevo texto, y reescribir la ultima linea
            borrar_ultima_linea()
            print_level(texto, mode)
            print(self.lastline)
        else:
            # aca deberia escribir el nuevo texto
            print_level(texto, mode)

    async def time_tracker(self):
        self.prprint("entered time_tracker", "debug")
        while True:
            for timer_id in range(len(self.timers) - 1):
                await self.gen_lastline(timer_id)
            # playsound(parentdir + "/sounds/sound_1.wav")
            # first_timer = 5
            # await self.gen_lastline(first_timer)
            # borrar_ultima_linea()
            # playsound(parentdir + "/sounds/sound_2.wav")
            self.count += 1
            # second_timer = 13
            await self.gen_lastline(len(self.timers) - 1)
            # self.lastline = f"[{genbar(0.2, '*')}] contador: {self.count}, se esperan 5"
            # # print(self.lastline)
            # self.refresh_lastline()
            # await asyncio.sleep(2)
            # borrar_ultima_linea()

    async def gen_lastline(self, timer_id):
        timer = self.timers[timer_id]
        time_count = timer
        timer_char = self.timer_chars[timer_id]

        # To play audio in background, use playsound module if not in windows
        winsound.PlaySound(None, winsound.SND_ASYNC)
        winsound.PlaySound(f"{self.parentdir}/sounds/sound_{timer_id % 2 + 1}.wav",
                           winsound.SND_ASYNC | winsound.SND_ALIAS)
        # playsound.playsound(f"{self.parentdir}/sounds/sound_{1}.wav", True)

        while time_count > 0:
            self.lastline = f"[{genbar(1 - time_count / timer, timer_char)}]: {timer - time_count}/{timer} || Phase: {timer_id + 1}/{len(self.timers)} || Epoc: {self.count}"
            # borrar_ultima_linea()
            self.refresh_lastline()
            await asyncio.sleep(1)
            time_count -= 1

    def refresh_lastline(self):
        if self.printed_before:
            borrar_ultima_linea()
        self.printed_before = True
        print(self.lastline)

    async def input_tracker(self):
        self.prprint("entered input_tracker", "debug")
        ya_logeado = False
        while True:
            result = await aioconsole.ainput()
            if result == "b":
                # break execution
                borrar_ultima_linea(2)
                if ya_logeado:
                    borrar_ultima_linea()
                self.lastline = ""
                return True
            else:
                borrar_ultima_linea()
                if not ya_logeado:
                    ya_logeado = True
                else:
                    borrar_ultima_linea()
                self.prprint(f"input: {result}", "info")


def get_valid_timers(args):
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
    args = sys.argv[1:]
    newargs = []
    for arg in args[1:]:
        if arg == "--debug":
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode activated")
        elif arg == "--info":
            logger.setLevel(logging.INFO)
            logger.info("Info mode activated")
        elif arg == "--warning":
            logger.setLevel(logging.WARNING)
            logger.warning("Warning mode activated")
        elif arg == "--error":
            logger.setLevel(logging.ERROR)
            logger.error("Error mode activated")
        elif arg == "--critical":
            logger.setLevel(logging.CRITICAL)
            logger.critical("Critical mode activated")
        else:
            newargs.append(arg)
    timers = get_valid_timers(newargs)
    if not timers:
        timers = [13, 5]
    # print(sys.argv)
    Clock(timers)