from modules import Doki8Checker, YuyunChecker

if __name__ == '__main__':
    checkers = [
        Doki8Checker(3, 60),
        YuyunChecker(3, 60),
    ]
    for checker in checkers:
        try:
            checker.run()
        except Exception as err:
            print(err)
