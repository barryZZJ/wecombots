import argparse
from pathlib import Path
from crontab import CronTab


# Define a function to register a python file to crontab
def register(fullpath: str, check_interval):
    # Create a CronTab object for the current user
    cron = CronTab(user=True)
    # Create a new cron job with the file name and the check interval
    job = cron.new(command=f'python3 {fullpath}')
    job.minute.every(check_interval)
    # Write the cron job to crontab
    cron.write()
    # Print a success message
    print(f'Registered {fullpath} to crontab with {check_interval} minutes interval.')

# Define a function to unregister a python file from crontab
def unregister(fullpath: str):
    # Create a CronTab object for the current user
    cron = CronTab(user=True)
    # Find and remove the cron job that matches the file name
    cron.remove_all(command=f'python3 {fullpath}')
    # Write the changes to crontab
    cron.write()
    # Print a success message
    print(f'Unregistered {fullpath} from crontab.')

# Define a function to list the relevant items in crontab
def list_items(fullpath: str):
    # Create a CronTab object for the current user
    cron = CronTab(user=True)
    # Find and print the cron jobs that match the file name
    for job in cron.find_command(f'python3 {fullpath}'):
        print(job)
        return
    # Print a message if no matching jobs are found
    print(f'No relevant items found for {fullpath} in crontab.')

def main():
    # Create an argument parser to parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='The python file to register or unregister from crontab.')
    parser.add_argument('-r', '--register', action='store_true', help='Register the file to crontab.')
    parser.add_argument('-u', '--unregister', action='store_true', help='Unregister the file from crontab.')
    parser.add_argument('-l', '--list', action='store_true', help='List the relevant items in crontab.')
    parser.add_argument("-i", "--interval", type=int, default=20, help="The check interval in minutes for the file to run. Default 20 minutes")
    args = parser.parse_args()

    args.fullpath = Path(args.file).resolve()
    assert args.fullpath.exists(), str(args.fullpath) + ' does not exists!'

    # Check if the register or unregister or list option is given
    if args.register:
        # Call the register function with the file and interval arguments
        register(str(args.fullpath), args.interval)
    elif args.unregister:
        # Call the unregister function with the file argument
        unregister(str(args.fullpath))
    elif args.list:
        # Call the list_items function with the file argument
        list_items(str(args.fullpath))
    else:
        # Print a usage message
        print('Please specify either -r, -u or -l option.')
