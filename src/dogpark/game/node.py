from dogpark.game.gamestate import GameState


class Node:
    def __init__(self, root=True, message=None, player=0):
        # A list of the child Nodes, found one level below in the game tree.
        # NOTE: this field has to be initialized by self.compute_and_get_children().
        self.children: list[Node] = []
        # The current state of the game. See the State class for more information.
        self.state: GameState = None
        # The parent Node in the game tree.
        self.parent: Node = None
        # The action that led to this node in the game tree, represented as an int.
        # Can be transformed to a string (e.g. "left") using ACTION_TO_STR in shared.py.
        self.move = None
        # This field can be ignored for this assignment.
        self.probability = 1.0

        if root:
            # Initialize the following fields:
            #   self.depth (the depth level at the current node - 0 at the root)
            #   self.player (the current player's index; MAX is 0 and MIN is 1)
            self.initialize_root(message, player)

    def add_child(self, state: State, move: int, depth: int = 0, observations: dict = {}, probability: float = 1.0):
        """
        Add a new node as a child of current node
        :param state: child's state
        :param move: child's move
        :param probability: probability of accessing child
        :param depth: depth of the child
        :observations: observations of the game
        :return:
        """
        new_node = self.__class__(root=False)
        new_node.state = state
        new_node.parent = self
        new_node.move = move
        new_node.depth = depth
        new_node.observations = observations
        self.children.append(new_node)

        new_node.probability = probability
        return new_node

    def initialize_root(self, curr_state, player):
        """
        Initialize root node.
        :param curr_state: parsed dict coming from game_controller
        :return:
        """

        self.depth = 0
        self.player = player  # Root's player
        obs = curr_state["observations"]
        keys = sorted(obs.keys())
        obs = np.array([np.array(obs[k]) for k in keys])
        obs = obs.T
        obs = {i: j.tolist() for i, j in enumerate(obs)}
        self.observations = obs
        # Translate message state into state object
        curr_state_s = State(len(curr_state["fishes_positions"].keys()))
        curr_state_s.set_player(self.player)
        curr_state_s.set_hook_positions(
            (*curr_state["hooks_positions"][0], *curr_state["hooks_positions"][1]))
        curr_state_s.set_caught(
            (curr_state["caught_fish"][0], curr_state["caught_fish"][1]))
        for i, f in curr_state["fishes_positions"].items():
            curr_state_s.set_fish_positions(i, f)

        # Set score of players
        player_scores = curr_state["player_scores"]
        curr_state_s.set_player_scores(player_scores[0], player_scores[1])

        # Set score, i.e. points, for fishes
        fish_scores = curr_state["fish_scores"]
        curr_state_s.set_fish_scores(fish_scores)

        self.state = curr_state_s  # Root's state object

    def compute_and_get_children(self) -> List[Node]:
        """
        Populate the node with its children. Then return them.
        :param:
        :return: list of children nodes
        """

        if len(self.observations) == self.depth:  # Cannot compute children any longer
            return []

        if len(self.children) != 0:  # If we already compute the children
            return self.children

        current_player = self.state.get_player()
        caught = self.state.get_caught()
        if caught[current_player] is not None:
            # Next action is always up for the current player
            new_state = self.compute_next_state(self.state, 1, self.observations[self.depth])
            self.add_child(new_state, 1, self.depth + 1, self.observations)
        else:
            # Any action is possible
            for act in range(5):
                new_state = self.compute_next_state(
                    self.state, act, self.observations[self.depth])
                self.add_child(new_state, act, self.depth + 1, self.observations)

        return self.children

    def compute_next_state(self, current_state, act, observations):
        """
        Given a state and an action, compute the next state. Add the next observations as well.
        :param current_state: current state object instance
        :param act: integer of the move
        :param observations: list of observations for current fish
        :return:
        """
        current_player = current_state.get_player()
        next_player = 1 - current_player
        fish_states = current_state.get_fish_positions()
        hook_states = current_state.get_hook_positions()
        new_state = State(len(fish_states.keys()))
        new_state.set_player(next_player)
        current_fishes_on_rod = current_state.get_caught()
        self.compute_new_fish_states(new_state, fish_states, observations, current_player,
                                     fishes_on_rod=current_fishes_on_rod)
        new_hook_positions = self.compute_new_hook_states(
            hook_states, current_player, ACT_TO_MOVES[act])
        new_state.set_hook_positions(new_hook_positions)

        # Get player scores for new state
        score_p0, score_p1 = current_state.get_player_scores()

        # Set fish scores for new state
        new_state.set_fish_scores(current_state.get_fish_scores())

        # Compute the fish that are currently caught by players
        next_caught_fish, pull_in_fishes = compute_caught_fish(new_state, current_fishes_on_rod)

        # Update player scores and remove fishes that are caught and at the surface
        fish_score_points = new_state.get_fish_scores()
        for i_player, fish_number in enumerate(pull_in_fishes):
            if fish_number is not None:
                if i_player == 0:
                    score_p0 += fish_score_points[fish_number]
                else:
                    score_p1 += fish_score_points[fish_number]

                # Remove fish
                new_state.remove_fish(fish_number)

        # Update players scores
        new_state.set_player_scores(score_p0, score_p1)

        new_state.set_caught(next_caught_fish)

        return new_state