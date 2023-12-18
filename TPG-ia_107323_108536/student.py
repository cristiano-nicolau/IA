"""Example client."""
import asyncio
import collections
import getpass
import json
import os

import websockets

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        
        # Class who represents the problem to be solved
        # Receives the game map, the initial position, the destination and the obstacles
        # See possible actions, valid states and the cost of each action, and calculate the heuristic
        class SearchProblem:            
            def __init__(self, game_map, initial, destination, obstacles):
                self.game_map = game_map
                self.initial = initial
                self.destination = destination
                self.obstacles = obstacles

            def goal_test(self, state):
                return state == self.destination

            def actions(self, state):
                x, y = state
                possible_actions = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                return [action for action in possible_actions if self.is_valid(action)]
            
            
            def is_under_rock(self, state):
                x, y = state
                return (x, y - 1) in self.obstacles

            def is_valid(self, state):
                x, y = state
                return (
                    0 <= x < len(self.game_map) and
                    0 <= y < len(self.game_map[0]) and
                    self.game_map[x][y] != '#' and
                    state not in self.obstacles and
                    not self.is_under_rock(state)
                )

            def result(self, state, action):
                return action

            def cost(self, state, action):
                return 1

            def heuristic(self, state):
                return abs(state[0] - self.destination[0]) + abs(state[1] - self.destination[1])
            

        # Class who represents the tree of the problem
        # Receives the problem and the initial state
        # Search for the solution using BFS
        # Returns the path to the solution
        class SearchTree:
            def __init__(self, problem):
                self.problem = problem
                self.frontier = collections.deque()
                self.frontier.append(self.problem.initial)
                self.explored = set()
                self.parents = dict()
                self.parents[self.problem.initial] = None

            def search(self):
                while self.frontier:
                    state = self.frontier.popleft()
                    if self.problem.goal_test(state):
                        return self.solution(state)
                    self.explored.add(state)
                    for action in self.problem.actions(state):
                        neighbor = self.problem.result(state, action)
                        if neighbor not in self.explored and neighbor not in self.frontier:
                            self.frontier.append(neighbor)
                            self.parents[neighbor] = state
                return None

            def solution(self, state):
                path = []
                while state is not None:
                    path.append(state)
                    state = self.parents[state]
                return path[::-1]
            
            
        def die(digdug_x, digdug_y, monster_x, monster_y, monster_direction):
            """Function to check if digdug dies in next postions possible"""

            if monster_direction in {0, 2}:
                return (
                    digdug_x == monster_x
                    and (digdug_y == monster_y or digdug_y + 2 == monster_y or digdug_y -2 == monster_y or digdug_y + 1 == monster_y or digdug_y - 1 == monster_y)
                )
            elif monster_direction == 1:
                return (
                    (digdug_x == monster_x or digdug_x + 1 == monster_x or digdug_x - 1 == monster_x or digdug_x + 2 == monster_x)
                    and digdug_y == monster_y
                )
            elif monster_direction == 3:
                return (
                    (digdug_x == monster_x or digdug_x + 1 == monster_x or digdug_x - 1 == monster_x or digdug_x - 2 == monster_x)
                    and digdug_y == monster_y
                )
            else:
                return False


        def determine_move_command(digdug_pos, next_step,monster_pos,name,dir):
            """Function to determine the move command"""

            if name == "Pooka" or (name=="Fygar" and (dir==0 or dir==2)):
                if digdug_pos[0] < next_step[0] :
                    if not die(digdug_pos[0]+1,digdug_pos[1],monster_pos[0],monster_pos[1],dir):
                        return "d"
                elif digdug_pos[0] > next_step[0]:
                    if not die(digdug_pos[0]-1,digdug_pos[1],monster_pos[0],monster_pos[1],dir):
                        return "a"
                elif digdug_pos[1] < next_step[1]:
                    if not die(digdug_pos[0],digdug_pos[1]+1,monster_pos[0],monster_pos[1],dir):
                        return "s"
                elif digdug_pos[1] > next_step[1]:
                    if not die(digdug_pos[0],digdug_pos[1]-1,monster_pos[0],monster_pos[1],dir):
                        return "w"
                else:
                    return ""
            else:
                if digdug_pos[0] < next_step[0] :
                     if dir!=3 and not die(digdug_pos[0],digdug_pos[1]-1,monster_pos[0],monster_pos[1],dir):
                        return "d"
                elif digdug_pos[0] > next_step[0]:
                    if dir!=1 and not die(digdug_pos[0],digdug_pos[1]-1,monster_pos[0],monster_pos[1],dir):
                        return "a"
                elif digdug_pos[1] < next_step[1]:
                        return "s"
                elif digdug_pos[1] > next_step[1]:
                        return "w"
                else:
                    return ""
                
            
        def find_closest_monster(digdug_pos, monsters):
            """Function to find the closest monster to digdug"""

            closest_monster = min(
                monsters,
                key=lambda monster: abs(digdug_pos[0] - monster["pos"][0]) + abs(digdug_pos[1] - monster["pos"][1])
            )

            return {
                "position": (closest_monster["pos"][0], closest_monster["pos"][1]),
                "name": closest_monster["name"],
                "direction": closest_monster.get("dir"),
                "fire": "fire" in closest_monster,
                "traverse": closest_monster.get("traverse", False), 
            }
        
        def is_monster_in_front(digdug_pos, monster_pos):
            """Function to check if there is a monster in front of digdug"""

            dx, dy = digdug_pos
            mx, my = monster_pos
            map_height = len(game_map)
            map_width = len(game_map[0])

            #Distance under 3 blocks
            if ((mx == dx and abs(my - dy) <= 3) or (my == dy and abs(mx - dx) <= 3)):
                #Vertical search
                if dx == mx: 
                    for y in range(min(dy, my) + 1, max(dy, my)):
                        if y < 0 or y >= map_height or dx < 0 or dx >= map_width or game_map[y][dx] != 0:
                            return False
                #Horizontal Search
                elif dy == my: 
                    for x in range(min(dx, mx) + 1, max(dx, mx)):
                        if x < 0 or x >= map_width or dy < 0 or dy >= map_height or game_map[dy][x] != 0:
                            return False
                        
                #Return True if monster in front
                return True


        def find_path(game_map, initial, destination, obstacles):
            """Function to find the path to a destination using SearchTree"""

            problem = SearchProblem(game_map, initial, destination, obstacles)
            tree = SearchTree(problem)
            path = tree.search()
            return path[1:] if path is not None else None
        
        
        def is_monster_near_digdug(digdug_pos, monsters_pos):
            """Function to check if there is a monster near digdug"""

            for monster_pos in monsters_pos:
                if abs(digdug_pos[0] - monster_pos[0]) <= 2 and abs(digdug_pos[1] - monster_pos[1]) <= 2:
                    return True
            return  False
        
        
        def upper_or_bellow(digdugpos,destination):
            """ Function to go up or down, depending on the position of the monster"""

            x, y = destination
            dx, dy = digdugpos
            if dx<x:
                if not die(digdug_pos[0]-1,digdug_pos[1],monster_pos[0],monster_pos[1],dir):
                    return "w"
            elif dx>x:
                if not die(digdug_pos[0]-1,digdug_pos[1],monster_pos[0],monster_pos[1],dir):
                    return "s"
            else:
                return "A"
            
            
        
        def avoid_monsters(digdug_pos, monster_pos, current_direction):
            """Function to avoid fire from fygar"""

            mx, my = monster_pos
            dx, dy = digdug_pos

            if mx == dx or my == dy:
                if current_direction == 0 and my < dy:
                    return "w"
                elif current_direction == 1 and mx > dx:
                    return "d"
                elif current_direction == 2 and my > dy:
                    return "s"
                elif current_direction == 3 and mx < dx:
                    return "a"

            else:
                return None


        def check_distance_and_avoid(digdug_pos, monster_pos, evasion_distance):
            """Function to check distance between digdug and monster"""

            distance = abs(digdug_pos[0] - monster_pos[0]) + abs(digdug_pos[1] - monster_pos[1])
            if distance < evasion_distance:
                    return "A" 
            return None



        
        last_actions = collections.deque(maxlen=2)
        monster_near_digdug_count = 0
    
        while True:

            try:
                # receive the game information and the current state of the game
                state = json.loads(await websocket.recv())
                print(state)

                # Extract relevant information from the state
                if "map" in state:
                   game_map=state["map"]
                   continue
                
                if "digdug" in state:
                    digdugx, digdugy = state["digdug"]
                    digdug_pos = (digdugx, digdugy)
                    print(f"DigDug position: {digdug_pos}")


                if "enemies" in state:
                    enemies = state["enemies"]
                    
                if "rocks" in state:
                    rock = state["rocks"]
                    rocks = [(rock["pos"][0], rock["pos"][1]) for rock in rock]
                    
                print(f"Rocks positions: {rocks}")   
                if enemies:
                    # Get the position of each monster
                    monsters_pos= [(monster["pos"][0], monster["pos"][1]) for monster in enemies]

                    # Get the closest monster to digdug
                    closest_monster_info = find_closest_monster(digdug_pos, enemies)

                    if closest_monster_info:
                            closest_monster_position = closest_monster_info["position"]
                            closest_monster_name = closest_monster_info["name"]
                            closest_monster_direction = closest_monster_info["direction"]
                        
                            print(f"Closest Monster Position: {closest_monster_position}")
                            print(f"Closest Monster Name: {closest_monster_name}")
                            print(f"Closest Monster Direction: {closest_monster_direction}")
                            

                            if closest_monster_name == "Fygar":
                                
                                fygar_x, fygar_y = closest_monster_position
                                rock_near_fygar = any(
                                    (fygar_x + dx, fygar_y) in rocks for dx in [-1, -2, 1, 2]
                                )

                                if rock_near_fygar:
                                    if digdug_pos[1] <= fygar_y:
                                        destination = (fygar_x, fygar_y + 2)
                                    else:
                                        destination = (fygar_x, fygar_y - 2)
                                else:
                                    
                                    if abs(digdug_pos[0] - closest_monster_position[0]) >= 3 or abs(digdug_pos[1] - closest_monster_position[1]) >= 3:
                                        destination = closest_monster_position
                                    else:
                                        # If monster is Fygar and is attacking fire, digdug should avoid it
                                        if "fire" in closest_monster_info:
                                            fire_direction = closest_monster_direction
                                            fire_position = (
                                                closest_monster_position[0] + 2 if fire_direction == 1 else closest_monster_position[0] - 2,
                                                closest_monster_position[1]
                                            )

                                            avoid_fire_direction = avoid_monsters(digdug_pos, fire_position, closest_monster_direction)
                                                                                        
                                            if avoid_fire_direction:
                                                destination = None
                                                action = avoid_fire_direction
                                            else:
                                                destination = (
                                                    closest_monster_position[0] + 2 if closest_monster_direction == 3 else
                                                    closest_monster_position[0] - 2 if closest_monster_direction == 1 else
                                                    closest_monster_position[0],
                                                    closest_monster_position[1]
                                                )
                                                
                                            if (digdug_pos[0]==closest_monster_position[0] + 2 or digdug_pos[0]==closest_monster_position[0] -2) and digdug_pos[1] == closest_monster_position[1]:
                                                destination=closest_monster_position 
                                        else:
                                            destination = closest_monster_position
                               
                            
                                        
                            elif closest_monster_name=="Pooka":
                                
                                # if monster is Poka and is a ghost, digdug should avoid it
                                if closest_monster_info["traverse"]  and abs(digdug_pos[0] - monster_pos[0]) + abs(digdug_pos[1] - monster_pos[1])<=6:
                                    if digdug_pos[1]<=closest_monster_position[1]:
                                        destination=(digdug_pos[0],1)
                                    else:
                                        destination=(digdug_pos[0],23)
                                else:
                                    # Calculate the destination based on the position of the monster
                                    if closest_monster_direction==0 or closest_monster_direction==2:
                                        if digdug_pos[1]<closest_monster_position[1]:
                                            destination=(closest_monster_position[0],closest_monster_position[1]-1)
                                        else:
                                            destination=(closest_monster_position[0],closest_monster_position[1]+1)
                                    else:
                                        destination=(closest_monster_position[0],closest_monster_position[1])
                                        
                                    # If digdug is in the same line or column as the monster, digdug should attack
                                    if digdug_pos[0] == closest_monster_position[0] or digdug_pos[1] == closest_monster_position[1]  :
                                        action = "A" 
                                    else:
                                        # If digdug is near the monster, digdug should avoid it
                                        avoid_direction = avoid_monsters(digdug_pos, closest_monster_position, closest_monster_direction)
                                        if avoid_direction:
                                            destination = None 
                                            action = avoid_direction
                                            
                                        distance_avoid = check_distance_and_avoid(digdug_pos, closest_monster_position, 3)
                                        if distance_avoid:
                                            destination = None
                                            action = avoid_direction
                                        
                
                # calculate the path to the destination using the SearchTree
                if destination is not None:
                    path_to_destination = find_path(game_map, digdug_pos,destination,rocks)
                    print(f"Path to destination: {path_to_destination}")

                # Determine the next action based on the calculated path and current game state
                if path_to_destination:
                    next_step = path_to_destination[0]
                    action = determine_move_command(digdug_pos, next_step,closest_monster_position,closest_monster_name,closest_monster_direction)
                    for monster in enemies:
                        monster_pos = (monster["pos"][0], monster["pos"][1])
                        # If there is a monster in front of digdug, digdug should attack
                        if is_monster_in_front(digdug_pos, monster_pos):
                            action = "A"  
                    print(f"Next step: {next_step}")
                
                
                # Check if there is a monster near digdug, and take appropriate action
                if is_monster_near_digdug(digdug_pos, monsters_pos):
                    monster_near_digdug_count += 1
                    last_actions.append(action)
                else:
                    monster_near_digdug_count = 0
                    last_actions.clear()
                    
                print(f"Last actions: {last_actions}")

                # If there are two monsters near digdug, and digdug is moving towards one, digdug should change direction to avoid getting killed
                if closest_monster_name=="Pooka":
                    if monster_near_digdug_count >= 2 and all(a in ("a", "d") for a in last_actions):
                        if digdug_pos[0] != closest_monster_position[0]:
                            act=upper_or_bellow(digdug_pos,destination)
                            action = act
                            monster_near_digdug_count = 0
                            last_actions.clear()
                
                # Ensure that the action is valid, and send it to the server
                if not action or action==None:
                    action=""
                    
                await websocket.send(json.dumps({"cmd": "key", "key": action}))
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
            
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))