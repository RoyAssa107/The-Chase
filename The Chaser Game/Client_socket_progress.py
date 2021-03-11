########################################
#         Written by: Roy Assa         #
#         ID: 322542226                #
########################################
import socket
import time
import numpy as np
from tabulate import tabulate

###############################################
###      Defining constants for Server      ###
###############################################
HEADER = 64
PORT = 5000  # Free port


class Player:

    ###############################################
    ###       Constructor of class Player       ###
    ###############################################
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.open_game = "YES"
        self.answer = ""
        self.balance = 0
        self.player_position = 0
        self.life_line = 1
        self.flag_already_played_a_game = 0

    #######################################################
    ###       Function that clears all attributes       ###
    #######################################################
    def ClearValues(self):
        self.open_game = "YES"
        self.answer = ""
        self.balance = 0
        self.player_position = 0
        self.life_line = 1

    ########################################################
    ###       Function that prints table of stage2       ###
    ########################################################
    def Print_Tabulate_Progress_Table_Stage_2(self):
        headers = ["Stage", "Progress"]

        rows = []
        for index in range(0, 8):
            if index == 0:
                rows.append([index, "Chaser"])
            elif index == 2:
                rows.append([index, int(self.balance) * 2])
            elif index == 3:
                rows.append([index, int(self.balance)])
            elif index == 4:
                rows.append([index, int(int(self.balance) / 2)])
            elif index == 7:
                rows.append([index, "Bank"])
            else:
                rows.append([index, " "])
            # rows.append(row)

        m = np.array(rows)
        # tabulate data
        # table = tabulate(m, headers, tablefmt="fancy_grid")
        table = tabulate(m, headers, tablefmt="pretty")
        # output
        print(table)

    #################################################################
    ###       Function that prints current progress in game       ###
    #################################################################
    def Print_Tabulate_Progress_Table(self, chaser_position):

        headers = ["Stage", "Progress"]

        rows = []
        for index in range(0, 8):
            if index == chaser_position:
                rows.append([index, "Chaser"])
            elif index == int(self.player_position):
                rows.append([index, "Player"])
            else:
                rows.append([index, ' '])

        m = np.array(rows)
        # tabulate data
        table = tabulate(m, headers, tablefmt="fancy_grid")
        # output
        print(table)
        self.balance = int(self.balance)

    ######################################################
    ###       Game method to proceed client game       ###
    ######################################################
    def Play_Game(self, flag_correct_answer_above_0, flag_player_choice):

        flag_winner = "None"  # Flag to represent the winner of the game

        ####################
        ##   Stage0 + 1   ##
        ####################

        while flag_correct_answer_above_0 == 0:
            if flag_player_choice == 1:  # If player already requested to start the new game (old player)
                status = self.client_socket.recv(1024).decode(FORMAT)
            else:
                print("Welcome to the game \"THE CHASE!!!\"\nWould you like to Start the game? (YES/NO)")
                while True:
                    self.open_game = input("Your choice: ")  # Get clients choice
                    if self.open_game.lower() != "no" and self.open_game.lower() != "yes":
                        print("Invalid input enetered!")
                    else:
                        break

                if self.open_game.lower() == "no":  # Checking if answer is no (doesn't want to continue play)
                    if self.flag_already_played_a_game == 1:
                        print("GOOD BYE :)")  # player doesnt want to play ==> end session (send 1 to server)
                        self.client_socket.send(str(self.flag_already_played_a_game).encode(FORMAT))
                    return 1

                elif self.flag_already_played_a_game == 1:  # Checking if player has already played a game
                    pass
                    continue_game = "2"  # Sending to server signal that client is ready to continue
                    self.client_socket.send(continue_game.encode(FORMAT))

                elif self.flag_already_played_a_game == 0:
                    # Client would like to start the game (checking if there are already 3 clients connected)
                    ######## CLIENT CONNECTING TO SERVER#######
                    try:
                        self.client_socket.connect(ADDR)  # Connecting to server in order to start game
                        status_from_server = str(self.client_socket.recv(1024).decode(FORMAT))  # Checking server status
                        time.sleep(0.1)
                        if status_from_server == "MAX REACHED!":
                            # Maximum players exceeded => disconnecting client from server
                            print("MAXIMUM PLAYERS EXCEEDED!")
                            return 1
                    except socket.error:
                        print("MAXIMUM PLAYERS EXCEEDED!!\nPLEASE JOIN LATER :)")
                        exit(-1)

            # Heading to stage 1 in the game (asking 3 random question)
            status = self.client_socket.recv(1024).decode(FORMAT)
            print(status)
            time.sleep(0.1)

            # Asking 3 Randomized questions
            for index in range(3):
                print(str(self.client_socket.recv(1024).decode(FORMAT)))  # Client received the question
                self.answer = input("Your answer: ")  # Client writes the answer
                self.client_socket.send(self.answer.encode(FORMAT))  # Client sending the answer to server

            flag_correct_answer_above_0 = self.client_socket.recv(1024).decode(FORMAT)
            if int(flag_correct_answer_above_0) == 0:
                print("YOU GOT ALL ANSWERS WRONG!!!\n")  # Sending back to beginning of stage
                flag_correct_answer_above_0 = 0
                self.flag_already_played_a_game = 1
                flag_player_choice = 0
                continue_game = "2"  # Client sending confirmation to continue
                self.client_socket.send(continue_game.encode(FORMAT))
                # time.sleep(2)
            else:
                continue_game = "2"  # Client sending confirmation to continue
                self.client_socket.send(continue_game.encode(FORMAT))
                self.client_socket.send(continue_game.encode(FORMAT))

        # Client passed first stage of the game successfully
        print("\nYou passed the first stage!")
        self.balance = self.client_socket.recv(1024).decode(FORMAT)  # Getting the balance from server
        print("Your balance after stage 1 is: {0}".format(self.balance))


        ################
        ##   Stage2   ##
        ################
        print("The game board status is the according:\n")
        self.Print_Tabulate_Progress_Table_Stage_2()  # Printing board of the game
        time.sleep(2)

        # Printing Stage2 instructions for player
        print("\nYou are in stage 2:\n"
              "Please choose one of the following options to continue:\n"
              "2. Start at level 2 for twice the  amount of money\n"
              "3. Start at level 3 for same amount of money\n"
              "4. Start at level 4 for half the amount of money\n")

        while True:
            player_choice = int(input("Your choice: "))  # Getting players choice (starting position on board)
            if player_choice is not 2 and player_choice is not 3 and player_choice is not 4:
                print("Invalid choice entered!!")
            else:
                break

        if player_choice == 2:
            self.balance = int(self.balance) * 2  # Player starting in level 2
        elif player_choice == 4:
            self.balance = int(self.balance) * 0.5  # Player starting in level 4

        # Sending starting position to server
        self.player_position = player_choice  # Players starting position on board (2/3/4)
        self.client_socket.send(str(self.player_position).encode(FORMAT))

        ################
        ##   Stage3   ##
        ################

        # Getting information about stage 3 from server
        print(self.client_socket.recv(1024).decode(FORMAT))

        while flag_winner == "None":  # Client is being asked questions until reached stage 7 of chaser gets him
            print(self.client_socket.recv(1024).decode(FORMAT))  # Client received the question
            self.answer = input("Your answer: ")  # Client writes the answer
            self.client_socket.send((self.answer).encode(FORMAT))  # Client sending the answer to server

            # Checking if player wants help (and still has 1 life_line left)
            if self.answer.lower() == "Help".lower() and self.life_line == 1:
                self.life_line = 0
                print(self.client_socket.recv(1024).decode(FORMAT))  # Client received the question(with 2 options only)

                while True:  # Checking that player doesnt request another help
                    self.answer = input("Your answer: ")  # Client writes the answer
                    if self.answer == str("help").lower():
                        print("You already requested help!")
                    else:
                        self.client_socket.send(self.answer.encode(FORMAT))  # Client sending the answer to server
                        break

            elif self.answer.lower() != "help":  # Checking if player requested help
                pass

            elif self.life_line == 0:  # Player doesnt have any more life_lines left (already used life_line)
                print("You already requested help!")
                while True:
                    self.answer = input("Your answer: ")  # Client writes the answer to the question
                    if self.answer == str("help").lower():
                        print("You already requested help!")
                    else:
                        self.client_socket.send(self.answer.encode(FORMAT))  # Client sending answer to the server
                        break

            # Printing player's information at this time of Stage 2
            information_client = self.client_socket.recv(1024).decode(FORMAT)
            print(information_client)

            # Getting status of game (if finished or not)
            flag_winner = self.client_socket.recv(1024).decode(FORMAT)

            # Printing current progress table of the game
            chaser_progress = int(self.client_socket.recv(1024).decode(FORMAT))
            self.player_position = int(self.client_socket.recv(1024).decode(FORMAT))

            self.Print_Tabulate_Progress_Table(chaser_progress)  # Printing current status of table

        # Game has ended. Here are the results:
        end_game_winner = (self.client_socket.recv(1024).decode(FORMAT))
        print(end_game_winner)

        # Checking if player wants to start a new game
        while True:
            another_game = input("Your choice: ")
            if another_game.lower() != "no" and another_game.lower() != "yes":
                print("Invalid input enetered!")
            else:
                break

        # Starting new game for client (if he requested so)
        self.client_socket.send(another_game.encode(FORMAT))  # Sending to server the client's choice
        if another_game.lower() == "yes":
            # Starting new game for client
            self.ClearValues()
            self.Play_Game(0, 1)  # Calling to this procedure to create new game for client
            return 1
        else:
            return 1  # Finished playing


##################################
###       MAIN PROGRAM         ###
##################################
if __name__ == "__main__":
    IP = socket.gethostbyname(socket.gethostname())  # Getting my own IP address
    ADDR = (IP, PORT)  # Creating a tuple of IP+PORT
    FORMAT = 'utf-8'  # Define the encoding format of messages from client-server

    client_player = Player()  # Creating new instance of a player (client)
    player_status = client_player.Play_Game(0, 0)  # Proceeding game of player (new client ==> sending 0 to method)
    while True:
        if player_status == 1:
            print("DISCONNECTED FROM SERVER:)")  # Player disconnected from server
            break
