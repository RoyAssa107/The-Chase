########################################
#         Written by: Roy Assa         #
#         ID: 322542226                #
########################################
import socket
import threading
import time
import random

###############################################
###      Defining constants for Server      ###
###############################################
HEADER = 64
PORT = 5000  # Free port


#########################################################
###      Helper function - executes Start_Game()      ###
#########################################################
def Continue_Play(connection, address):
    Start_Game(connection, address)
    return 0


######################################################################################################
###      Function that sends question to client and returning (to server) the correct answer       ###
######################################################################################################
def Ask_Question(connection, question_counter, random_question, stage):
    questions_part_1 = ["Is Java a type of OS?",
                        "Which animal can be seen on the Porsche logo?",
                        "Which country produces the most coffee in the world?",
                        "Which country invented tea?",
                        "Which kind of alcohol is Russia is notoriously known for?",
                        "Which country is responsible for giving us pizza and pasta?",
                        "Which organ has four chambers?",
                        "What is your body’s largest organ?",
                        "What kind of cells are found in the brain?",
                        "Which element is said to keep bones strong?"]

    answers_part_1 = [["No"], ["horse"], ["Brazil"],
                      ["China"], ["Vodka"], ["Italy"],
                      ["Heart"], ["Skin"], ["Neurons"], ["Calcium"]]

    questions_part_3 = ["What color is the \'black box\' in an aeroplane?\n"
                        "A. Black        B. Orange\n"
                        "C. Purple       D. Green",
                        "What is the Roman numeral for 1000?\n"
                        "A. M        B. IIVX\n"
                        "C. VXM      D. MIT",
                        "Which is the world's largest ocean?\n"
                        "A. Atlantic       B. Indian\n"
                        "C. Pacific        D. Antarctic",
                        "What is the capital city of Spain?\n"
                        "A. Barcelona        B. Bilbao\n"
                        "C. Sevilia          D. Madrid",
                        "What is the smallest country in the world at only 0.44 sq.km?\n"
                        "A. Pennsylvania       B. Michigan\n"
                        "C. Vatican city       D. Israel",
                        "What is the capital city of Sweden?\n"
                        "A. Copenhagen         B. Oslo\n"
                        "C. Stockholm          D. Tel-Aviv",
                        "What is the most common color uniform worn at Wimbledon?\n"
                        "A. White            B. Blue\n"
                        "C. Orange           D. Black",
                        "What is the highest score you can reach in 10 pin bowling?\n"
                        "A. 200            B. 100\n"
                        "C. 150            D. 300",
                        "What sport that has been played on the moon?\n"
                        "A. Tennis            B. Golf\n"
                        "C. Basketball        D. VolleyBall",
                        "Which country was the host nation for the 1966 World Championship in football for men?\n"
                        "A. Turkey          B. Israel\n"
                        "C. USA             D. England",
                        "How many Earths could fit inside the sun?\n"
                        "A. 3          B. 3000\n"
                        "C. 13,000     D. 1.3 million",
                        "Which country consumes the most chocolate per capita?\n"
                        "A. Swizerland       B. Norway\n"
                        "C. USA              D. Israel",
                        "When Michael Jordan played for the Chicago Bulls, how many NBA Championships did he win?\n"
                        "A. 4            B. 5\n"
                        "C. 6            D. 7",
                        "Which F1 racer holds the record for the most Grand Prix wins?\n"
                        "A. Lewis Hamilton       B. Michael Shumacher\n"
                        "C. Sebastian Vettel     D. Charles Lecler",
                        "What is often seen as the smallest unit of memory?\n"
                        "A. Bit           B. Byte\n"
                        "C. Terabyte      D. Kilobyte"]

    possible_answers_part_3_help = ["A. Black             B. Orange",
                                    "A. M                 C. VXM",
                                    "C. Pacific           D. Antarctic",
                                    "C. Sevilia           D. Madrid",
                                    "B. Michigan          C. Vatican city",
                                    "A. Copenhagen        C. Stockholm",
                                    "A. White             B. Blue",
                                    "A. 200               D. 300",
                                    "A. Tennis            B. Golf",
                                    "C. USA               D. England",
                                    "B. 3,000             D. 1.3 million",
                                    "A. Swizerland        B. Norway",
                                    "C. 6                 D. 7",
                                    "A. Lewis Hamilton    B. Michael Shumacher",
                                    "B. Byte              D. Kilobyte"]

    answers_part_3 = [["B"], ["A"], ["C"],
                      ["D"], ["C"], ["C"],
                      ["A"], ["D"], ["B"],
                      ["D"], ["D"], ["A"],
                      ["C"], ["A"], ["D"]]

    # Asking question at stage 1
    if stage == 1:
        question = ((str(questions_part_1[random_question])).replace('[\'', '')).replace('\']', '')
        correct_answer = ((str(answers_part_1[random_question])).replace('[\'', '')).replace('\']', '')

    # Asking question at stage 3 (==> The chase)
    elif stage == 3:
        question = ((str(questions_part_3[random_question])).replace('[\'', '')).replace('\']', '')
        correct_answer = ((str(answers_part_3[random_question])).replace('[\'', '')).replace('\']', '')

    # Asking question after player demanded help (assigned as "stage 10")
    elif stage == 10:
        question = ((str(possible_answers_part_3_help[random_question])).replace('[\'', '')).replace('\']', '')
        correct_answer = ((str(answers_part_3[random_question])).replace('[\'', '')).replace('\']', '')

    # Question for client
    connection.send(f"\nQuestion {question_counter + 1}:\n{question}".encode(FORMAT))

    return correct_answer  # Return to server the correct answer


####################################################################################
#  method that will enable the server to handle multiple clients connecting to it  #
#  This method will run "Simultanousely" for each client                           #
####################################################################################
def Start_Game(connection, address):

    print(f"[NEW CONNECTION] {address} connected.")  # Printing initial connection status

    #####################################
    ###     Declaring variables       ###
    #####################################
    asked_questions = []  # List that holds the question already asked
    money_balance_for_client = 0  # variable that holds current balance of player
    correct_answer_counter = 0  # Variable that holds #Correct answers
    continue_play_client = 0  # Variable that holds players choice of continuing or exiting the game
    flag_correct_answer_above_0 = 0  # variable that holds current balance of player
    flag_winner = "None"  # variable that holds the winner of the game
    chaser_progress = 0  # variable that holds stage of CHASER in table
    player_progress = 0  # variable that holds stage of PLAYER in table
    life_line_left = 1  # variable that holds amount of life lines left for player

    # Checking if maximum amount of players reached (currently 3 playing)
    if threading.activeCount() - 1 == 4:
        print("MAXIMUM PLAYERS EXCEEDED!")
        print(f"[CONNECTION CLOSED SUCCESSFULLY] for: {address}\n")
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}\n")  # printing the amount of threads working
        print("WAITING FOR CLIENTS TO CONNECT!")
        connection.send("MAX REACHED!".encode(FORMAT))
        time.sleep(2)
        connection.close()  # closing connection from client
        return 0
    else:
        connection.send("OK".encode(FORMAT))
        time.sleep(0.1)

    ################
    ##   Stage1   ##
    ################

    while flag_correct_answer_above_0 == 0:  # Checking if player hasn't passed stage1
        connection.send("\nLet us begin Stage 1:\n"
                        "You will be asked 3 question.".encode(FORMAT))  # Sending initial instructions to player

        # random_question = random.uniform(0, 100)  # randomizing question to client
        for index in range(3):
            while True:  # making sure that we randomize new question
                random_question = (int(random.uniform(0, 100)) % 10)  # randomizing question to client
                if random_question not in asked_questions:  # Checking new question that hasn't been asked previously
                    asked_questions.append(random_question)
                    break

            correct_answer = Ask_Question(connection, index, random_question, 1)  # Getting new question
            client_answer = connection.recv(1024).decode(FORMAT)  # Receive answer from client

            if str(client_answer).lower() == correct_answer.lower():
                money_balance_for_client += 5000  # correct answer will add 5,000 to client's balance
                correct_answer_counter += 1

        if correct_answer_counter != 0:
            flag_correct_answer_above_0 = 1
        else:
            # All answers are wrong!
            asked_questions = []  # Resetting all data of player
            correct_answer_counter = 0
            money_balance_for_client = 0

        # Sending status of correct answers to client
        connection.send(str(flag_correct_answer_above_0).encode(FORMAT))

        # Continue/Stop playing client (after all wrong answers from client)
        # 1 == no , 2 == yes
        continue_play_client = connection.recv(1024).decode(FORMAT)
        time.sleep(0.1)
        continue_play_client = connection.recv(1024).decode(FORMAT)
        if int(continue_play_client) == 1:  # Checking if client wants to play another game
            print("CLOSING CONNECTION!!")
            time.sleep(3)
            connection.close()  # closing connection from client
            print(f"[CONNECTION CLOSED SUCCESSFULLY] for: {address}\n")
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}\n")  # printing the amount of threads working
            print("WAITING FOR CLIENTS TO CONNECT!")
            return 0

    # Passed stage 1 successfully (#correct answers is above 0)
    print(f"{address} Balance: {money_balance_for_client}")
    connection.send(str(money_balance_for_client).encode(FORMAT))  # sending balance to client

    ################
    ##   Stage3   ##
    ################

    player_progress = int(connection.recv(1024).decode(FORMAT))  # receive starting position of client (of his choice)

    # Updating balance of player after his chosen starting position on board
    if player_progress == 2:
        money_balance_for_client = money_balance_for_client * 2
    elif player_progress == 4:
        money_balance_for_client = money_balance_for_client * 0.5

    # Sending information about new stage to client
    connection.send("\nLet us begin Stage 3:\n"
                    "You will be asked question with 4 possible answers.\n"
                    "Enter A/B/C/D for answer of enter \"Help\" for help (only 1 allowed!)\n".encode(FORMAT))

    question_counter = 0  # Initiate question counter

    while player_progress > chaser_progress and player_progress != 7:
        while True:  # making sure that we randomize new question
            random_question = (int(random.uniform(0, 100)) % 15)  # randomizing question to client
            if random_question not in asked_questions:
                asked_questions.append(random_question)
                break

        # Calling function that sends question to server
        # Asking client a question and getting correct answer from method
        correct_answer = Ask_Question(connection, question_counter, random_question, 3)
        client_answer = str(connection.recv(1024).decode(FORMAT))  # Receive answer from client

        # Checking if player has life_line left
        if client_answer.lower() == "help" and life_line_left == 1:
            life_line_left = 0
            correct_answer = Ask_Question(connection, question_counter, random_question, 10)
            client_answer = connection.recv(1024).decode(FORMAT)  # Receive answer from client (of 2 possibilities)

            if str(client_answer).lower() == "help":  # Checking if client asked for another help
                client_answer = str(connection.recv(1024).decode(FORMAT))

        # Player hasn't asked for another help
        elif client_answer.lower() != "help":
            pass

        # Receive answer from client (of 2 possibilities)
        elif life_line_left == 0:
            client_answer = str(connection.recv(1024).decode(FORMAT))

        # Checking if player answered correctly
        if str(client_answer).lower() == correct_answer.lower():
            player_progress += 1

        # Randomize correct answer of chaser using uniform distribution
        random_chaser_answer = int(random.uniform(1, 100))
        if random_chaser_answer <= 75:
            chaser_progress += 1

        # Checking if player reached to stage 7 ==> Won
        if player_progress == 7:
            flag_winner = "player"
        if player_progress == chaser_progress:
            flag_winner = "chaser"

        # sending information to client
        message = f"Your balance is: {money_balance_for_client}\n" \
                  f"Player is at stage: {player_progress}\n" \
                  f"Chaser is at stage: {chaser_progress}\n" \
                  f"Life line on board: {life_line_left}\n"

        question_counter += 1  # Increment question counter

        # Printing status of board (4 criteria according to instructions)
        connection.send(str(message).encode(FORMAT))  # Sending client his condition at this time
        time.sleep(0.1)

        # Sending to client the status of winner (of none of them still)
        connection.send(str(flag_winner).encode(FORMAT))
        time.sleep(0.1)

        # Sending Chaser's position to client
        connection.send(str(chaser_progress).encode(FORMAT))
        time.sleep(0.1)

        # Sending Player's position to client
        connection.send(str(player_progress).encode(FORMAT))
        time.sleep(0.1)

    # Checking who won the game
    if flag_winner == "chaser":
        end_game_winner = "The chaser won the game!!!\n" \
                          "Would you like to play another game?\n"
        connection.send(end_game_winner.encode(FORMAT))
    else:
        end_game_winner = "The Player won the game!!!\n" \
                          "Would you like to play another game?\n"
        connection.send(end_game_winner.encode(FORMAT))

    # Receive yes/no from client to whether he would like to play another game
    another_game = str(connection.recv(1024).decode(FORMAT))

    if (another_game).lower() == "yes":
        Start_Game(connection, address)  # Continue for another game
    else:
        print(f"\n[CLOSING CONNECTION] for: {address}")  # Closing connection for client
        time.sleep(3)
        connection.close()  # closing connection from client
        print(f"[CONNECTION CLOSED SUCCESSFULLY] for: {address}\n")
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}\n")  # printing the amount of threads working
        print("WAITING FOR CLIENTS TO CONNECT!")
        return


########################################################
###       Game method to proceed clients games       ###
########################################################
def Start():
    server_socket.listen(3)  # Limiting amount of users playing in parallel
    print(f"[LISTENING] server is listening on {IP}")
    while True:
        if threading.activeCount() == 0:  # Checking if this is the first player in total
            print("WAITING FOR CLIENTS TO CONNECT!!!")
        connection, address = server_socket.accept()  # Waiting for client to connect to server

        thread = threading.Thread(target=Start_Game, args=(connection, address))  # Creating new Thread object.
        # passing the handle func and full address to thread constructor

        thread.start()  # Starting the new thread (new client)
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}\n")  # printing the amount of threads working
        # on this process (opening another thread for next client to come!)


##############################
###     Main of server     ###
##############################
if __name__ == "__main__":
    IP = socket.gethostbyname(socket.gethostname())  # Getting my own (local) IP address
    ADDR = (IP, PORT)  # creating a tuple of IP+PORT
    FORMAT = 'utf-8'  # Define the encoding format of messages from client-server
    DISCONNECTED_MESSAGE = "DISCONNECTED"

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Opening Server socket
    server_socket.bind(ADDR)  # Binding server's socket with the tuple ADDR (IP,PORT)

    print("[Starting] server is starting...")
    Start()
    print("THE END!")
    exit(0)
