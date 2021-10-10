
class Grid:
    def create_grid(self, size=5):
        'creates a new grid by taking size as input'
        grid = []
        for _ in range(size):
            grid.append(['-'] * size)
        return grid


class GameEndedException(Exception):
    'created new type of exception to be used later'
    pass


class Game:
    size = 5
    grid = []
    is_input_taken = False
    players = ['A', 'B']
    
    def __init__(self):
        self.grid = Grid.create_grid(self.size)
        self.is_input_taken = False

    def exists_in_grid(self, player):
        'Check whether a player exists in grid, so we can find if they are lost'
        for row in self.grid:
            for character in row:
                if character[0] == player[0]:
                    return True
        return False

    def print_grid(self):
        'this function prints the grid'
        print('Current Grid:')
        for row in self.grid:
            print('\t'.join(row))
        print()
        if self.is_input_taken:
            A_exists = self.exists_in_grid('A')
            B_exists = self.exists_in_grid('B')
            if (not A_exists) or (not B_exists):
                # some player got characters empty (lost the match)
                winner = 'Nobody'
                if A_exists:
                    winner = 'A'
                elif B_exists:
                    winner = 'B'
                print(winner + ' won')
                raise GameEndedException()  # end the current game

    def has_duplicates(self, inp):
        'Check whether the user input has duplicates'
        # Time complexity: O(n*log(n))
        arr = inp[:]  # take copy of input
        arr.sort()
        for i in range(1, len(arr)):
            if arr[i-1] == arr[i]:  # if consecutive elements are same
                return True
        return False

    def add_to_grid(self, inp, player):
        'Adds some characters to the grid'
        for i in range(self.size):  # add player ID to characters
            inp[i] = player + '-' + inp[i]
        if player == self.players[0]:
            self.grid[-1] = inp  # add to last row
        else:
            self.grid[0] = inp  # add to 1st row

    def is_invalid_character(self, character):
        'Check whether it is an invalid character'
        if len(character) != 2:
            return True
        if not character[0].isalpha():
            return True
        if not character[1].isnumeric():
            return True
        return False

    def has_invalid_characters(self, inp):
        'Check whether there are any invalid characters in the user input'
        for character in inp:
            if self.is_invalid_character(character):
                print('Invalid character ' + character + '. Please try again')
                return True

    def take_input_positions(self, player):
        'Take user input for character positions'
        # keep trying until input is valid
        while 1:
            try:
                inp = input('Player' + player + ' input: ')
                # comma should be present 4 times (size-1)
                if inp.count(', ') != self.size-1:
                    print('Invalid input format. Please try again')
                    continue
                inp = inp.split(', ')
                if len(inp) != self.size:
                    print('Invalid number of characters. Pease try again')
                    continue
                if self.has_invalid_characters(inp):
                    continue
                if self.has_duplicates(inp):
                    print('Same character cannot appear multiple times. Please try again')
                    continue
                self.add_to_grid(inp, player)
                self.print_grid()
                return inp
            except KeyboardInterrupt:
                return False
            except Exception:
                continue

    def get_position(self, character):
        'Get the position of a specified character'
        for col in range(self.size):
            for row in range(self.size):
                if self.grid[col][row] == character:
                    return [row, col]
        return False

    def move(self, coords, dir, player):
        'Moves a character in a specified direction, returns new location'
        # directions are opposite for each player
        if player == self.players[0]:
            dist = 1
        else:
            dist = -1
        for char in dir:
            if 'L' == char:  coords[0] -= dist  # row -= 1
            elif 'R' == char:    coords[0] += dist  # row += 1
            elif 'F' == char:    coords[1] -= dist  # col -= 1
            elif 'B' == char:    coords[1] += dist  # col += 1
        return coords
    
    def invalid_dir(self, dir, char, kill):
        if char[0] == 'P' and dir != 'F':
            return True
        if char == 'H1' and len(kill) != 1:
            return True
        if char == 'H2':
            if len(kill) != 2:
                return True
            if kill[0] == kill[1]:  # if 2 x same direction
                return True
            if kill in ['RL', 'FB']:  # opposite directions
                return True
        if char == 'H3':
            if len(dir) != 3:
                return True
            if dir[0] == dir[2]:  # if 2 x same direction
                return True
            if dir[1:] in ['RL', 'FB']:
                return True
        for char in dir:
            if char not in 'LRFB':
                return True
        return False

    def make_move(self, char, dir, player, kill=''):
        'Makes a move in a specified direction'
        coord = self.get_position(player + '-' + char)
        if not coord:
            return 'Entered character does not exist. Please try again'
        # char can move only in supported direction
        if self.invalid_dir(dir, char, kill):
            return 'Invalid move for that character. Please try again. ' + str(char) + ' ' + str(dir) + ' ' + str(kill)
        
        new_coord = self.move(coord[:], dir, player)  # make copy of coord
        x = new_coord[0]
        y = new_coord[1]
        if x < 0 or x >= self.size:
            return 'Invalid move. Character may go out of the grid. Please try again. x: ' + str(x)
        if y < 0 or y >= self.size:
            return 'Invalid move. Character may go out of the grid. Please try again. y: ' + str(y)
        if self.grid[y][x][0] == player:
            return 'Targeted a character from your own team. Please try again'
        
        if kill:
            kill_coord = self.move(coord[:], kill, player)
            self.grid[kill_coord[1]][kill_coord[0]] = '-'  # make kill position empty
        # make the move
        self.grid[y][x] = player + '-' + char
        self.grid[coord[1]][coord[0]] = '-'  # make old position empty
        return None  # no error

    def take_input_move(self, player):
        'Takes a movement input from the user'
        while 1:
            inp = input('Player ' + player + '\'s move: ')  # Player A's move
            try:
                if inp.count(':') != 1:
                    print('Invalid input format. Please try again. Check :')
                    continue
                char, dir = inp.split(':')
                if not char or not dir:
                    print('Invalid input format. Please try again. Check character, direction')
                    continue
                if self.is_invalid_character(char):
                    print('Invalid character ' + char + '. Please try again')
                    continue
                if char == 'H3':
                    dir = dir[0] + dir[0] + dir[1]
                    error = self.make_move(char, dir, player)
                elif char[0] == 'H':  # if hero, make move again
                    error = self.make_move(char, dir*2, player, kill=dir)
                else:
                    error = self.make_move(char, dir, player)
                if error:
                    print(error)
                    continue
                break
            except KeyboardInterrupt:
                return False
            except Exception as e:
                print('Error:', e)
        self.print_grid()

    def start_game(self):
        'Starts the game'
        # global is_input_taken
        self.is_input_taken = False
        for player in self.players:
            # try to take input. if KeyboardInterrupt, return
            if not self.take_input_positions(player):
                return False
        self.is_input_taken = True
        try:
            while 1:
                for player in self.players:
                    self.take_input_move(player)
        except KeyboardInterrupt:
            return False
        except Exception:
            pass


if __name__ == '__main__':
    continueGame = True
    while continueGame:
        try:
            new_game = Game()
            continueGame = new_game.start_game()
            raise GameEndedException()
        except KeyboardInterrupt:
            continueGame = False
        except GameEndedException:
            continueGame = False
            try:
                try_again = input('\nDo you want to play again? Y/N: ')
                if 'Y' in try_again.upper():
                    continueGame = True
            except:
                pass
        except Exception:
            print('Game ended')
            continueGame = False
    print('\n\nThank you for playing the game')