import hardest_game
import random
from math import exp, sqrt
import matplotlib.pyplot as plt

def play_game_AI(str, map_name='map2.txt'):
    game = hardest_game.Game(map_name=map_name, game_type='AI').run_AI_moves_graphic(moves=str)
    return game


def simulate(str, map_name='map2.txt'):
    game = hardest_game.Game(map_name=map_name, game_type='AI').run_AI_moves_no_graphic(moves=str)
    return game


def run_whole_generation(list_of_strs, N, map_name='map2.txt'):
    game = hardest_game.Game(map_name=map_name, game_type='AIS').run_generation(list_of_moves=list_of_strs, move_len=N)
    return game


def play_human_mode(map_name='map2.txt'):
    hardest_game.Game(map_name=map_name, game_type='player').run_player_mode()


def get_initial_population(population_count, initial_length):
    population = []
    for i in range(population_count):
        population.append(''.join((random.choice(['w', 's', 'a', 'd', 'x']) for x in range(initial_length))))
    return population


def check_if_gene_is_good(game_list, must_eaten_goal_in_part):
    players_list = game_list.players
    goal_player = game_list.goal_player
    for player_index, player in enumerate(players_list):
        eaten_goal = 0
        for row in goal_player:
            if row[player_index]:
                eaten_goal += 1
        if must_eaten_goal_in_part == eaten_goal:
            if player[1] == -1:
                return True, player_index
    return False, None


def length_mutation(genes, length_mutation_probability=1 / 5, increase_length=15):
    probability = random.random()
    new_genes = []
    gene_size = len(genes[0])
    if probability <= length_mutation_probability:
        for gene in genes:
            new_gene = ''.join((random.choice(['w', 's', 'a', 'd', 'x']) for x in range(increase_length)))
            new_gene = gene + new_gene
            new_genes.append(new_gene)
        print('length_mutation')
        return gene_size + increase_length, new_genes
    return gene_size, genes


def all_goal_eaten_by_player(player_index, goal_player):
    for row in goal_player:
        if not row[player_index]:
            return False
    return True


def get_distance(x_1, y_1, x_2, y_2):
    return sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2)


def find_player_distance_to_goals(player, player_index, goal_player, goals):
    distance = 0
    player_x = player[0].x
    player_y = player[0].y
    for goal_index, row in enumerate(goal_player):
        if not row[player_index]:
            goal_x = goals[goal_index][0].x
            goal_y = goals[goal_index][0].y
            distance += get_distance(player_x, player_y, goal_x, goal_y)
    return distance


def find_player_distance_to_end(player, game_end):
    player_x = player[0].x
    player_y = player[0].y
    # end_x = game_end.x + game_end.w / 2
    # end_y = game_end.y + game_end.h / 2

    end_x = game_end.x
    end_y = game_end.y
    return get_distance(player_x, player_y, end_x, end_y)

def find_distance_from_start(player, start_x, start_y):
    player_x = player[0].x
    player_y = player[0].y
    return get_distance(player_x, player_y, start_x, start_y)


def get_fitness(player, player_index, goal_player, goals, game_end, start_x , start_y, lost_constant=0.9, win_constant=None):
    # distance = find_player_distance_to_goals(player, player_index, goal_player, goals)
    # fitness = 200 * exp(-0.009 * distance)
    #
    # if player[1] != -1:
    #     return fitness /
    if player[2]:
        return win_constant
    if all_goal_eaten_by_player(player_index, goal_player):
        distance = find_player_distance_to_end(player, game_end)
        return 2000 * exp(-0.06 * distance)
        # return 1000 * exp(-0.005 * find_player_distance_to_end(player, game_end))

    distance = find_player_distance_to_goals(player, player_index, goal_player, goals)
    distance_from_start = find_distance_from_start(player, start_x , start_y)
    fitness = 2000 * exp(-0.03 * distance) + distance_from_start
    # fitness = 80 * exp(-0.009 * distance) + distance_from_start
    # fitness = distance_from_start - distance
    return fitness


def get_players_fitness(game_list):
    players_list = game_list.players
    goal_player = game_list.goal_player
    goals = game_list.goals
    game_end = game_list.end
    start_x = game_list.player_x
    start_y = game_list.player_y
    players_fitness = []
    for player_index, player in enumerate(players_list):
        fitness = get_fitness(player, player_index, goal_player, goals, game_end, start_x, start_y)
        players_fitness.append(fitness)
    return players_fitness


def selection(genes, gene_fitness):
    sum_all_fitness = sum(gene_fitness)
    genes_probability = [x / sum_all_fitness for x in gene_fitness]
    selected_population = random.choices(genes, genes_probability, k=len(genes))
    return selected_population


def cross_over_two_gene(gene_1, gene_2, change_gene_from_index):
    random_place = random.randint(0, len(gene_1) - 1)
    while random_place <= change_gene_from_index:
        random_place = random.randint(0, len(gene_1) - 1)
    new_gene_1 = gene_1[:random_place] + gene_2[random_place:]
    new_gene_2 = gene_2[:random_place] + gene_1[random_place:]
    return new_gene_1, new_gene_2


def cross_over(genes, change_gene_from_index):
    random.shuffle(genes)
    new_genes = []
    for i in range(int(len(genes) / 2)):
        gene_1 = genes[i * 2]
        gene_2 = genes[i * 2 + 1]
        new_gene_1, new_gene_2 = cross_over_two_gene(gene_1, gene_2, change_gene_from_index)
        new_genes.append(new_gene_1)
        new_genes.append(new_gene_2)
    return new_genes


def mutate_gene(gene, change_gene_from_index):
    random_place = random.randint(0, len(gene) - 1)
    while random_place <= change_gene_from_index:
        random_place = random.randint(0, len(gene) - 1)
    new_char = random.choice(['w', 'a', 's', 'd', 'x'])
    mutated_gene = gene[:random_place - 1] + new_char + gene[random_place:]
    return mutated_gene


def mutation(genes, change_gene_from_index, mutation_probability=1 / 3, mutate_count=4):
    new_genes = []
    for gene in genes:
        new_gene = gene
        for mutate in range(mutate_count):
            probability = random.random()
            if probability <= mutation_probability:
                new_gene = mutate_gene(new_gene, change_gene_from_index)
        new_genes.append(new_gene)
    return new_genes


def improve_lost_gene(game_list, players_fitness, improve_from_best=0.1):
    players = game_list.players
    not_lost_fitness = []
    new_players_fitness = []
    for player_index, player in enumerate(players):
        if player[1] == -1:
            not_lost_fitness.append(players_fitness[player_index])

    if len(not_lost_fitness) == 0:
        return None

    mean_not_lost_fitness = sum(not_lost_fitness) / len(not_lost_fitness)
    best_not_lost_fitness = max(not_lost_fitness)
    for player_index, player in enumerate(players):
        if player[1] == -1:
            new_players_fitness.append(players_fitness[player_index])
            continue
        if (players_fitness[player_index] - mean_not_lost_fitness) / mean_not_lost_fitness > improve_from_best:
            new_players_fitness.append(best_not_lost_fitness)
            continue
        new_players_fitness.append(0)
    return new_players_fitness


def get_out_from_hell(genes, from_where, change_gene_from_index):
    last_from_where = -(len(genes[0]) - change_gene_from_index)
    from_where = max(from_where, last_from_where)
    genes_with_deleted_end = [x[:from_where] for x in genes]
    new_genes = []
    for gene in genes_with_deleted_end:
        new_genes.append(gene + ''.join((random.choice(['w', 's', 'a', 'd']) for x in range(-from_where))))

    return new_genes


def y_splash(genes, splash_count=20):
    new_genes = []
    quarter = int(len(genes) / 4)
    for gene in genes[:quarter]:
        new_genes.append(gene + ''.join(['w'] * splash_count) + ''.join(['d'] * int(splash_count / 2)))
    for gene in genes[quarter: 2 * quarter]:
        new_genes.append(gene + ''.join(['w'] * splash_count) + ''.join(['a'] * int(splash_count / 2)))

    for gene in genes[quarter * 2: quarter * 3]:
        new_genes.append(gene + ''.join(['s'] * splash_count) + ''.join(['a'] * int(splash_count / 2)))
    for gene in genes[quarter * 3:]:
        new_genes.append(gene + ''.join(['s'] * splash_count) + ''.join(['d'] * int(splash_count / 2)))
    return new_genes


def x_splash(genes, splash_count=20):
    new_genes = []
    quarter = int(len(genes) / 4)
    for gene in genes[:quarter]:
        new_genes.append(gene + ''.join(['a'] * splash_count) + ''.join(['w'] * int(splash_count / 2)))
    for gene in genes[quarter: 2 * quarter]:
        new_genes.append(gene + ''.join(['a'] * splash_count) + ''.join(['s'] * int(splash_count / 2)))

    for gene in genes[quarter * 2: quarter * 3]:
        new_genes.append(gene + ''.join(['d'] * splash_count) + ''.join(['w'] * int(splash_count / 2)))
    for gene in genes[quarter * 3:]:
        new_genes.append(gene + ''.join(['d'] * splash_count) + ''.join(['s'] * int(splash_count / 2)))
    return new_genes

def splash(genes, game_list, splash_probability=0.1, splash_count=50):
    players = game_list.players
    players_x_dict = {}
    players_y_dict = {}
    for player in players:
        players_x = int(player[0].x / 5)
        players_y = int(player[0].y / 5)
        if players_x in players_x_dict:
            players_x_dict[players_x] = players_x_dict[players_x] + 1
        else:
            players_x_dict[players_x] = 1

        if players_y in players_y_dict:
            players_y_dict[players_y] = players_y_dict[players_y] + 1
        else:
            players_y_dict[players_y] = 1

    if max(players_y_dict.values()) / len(genes) > 0.6:
        probability = random.random()
        if probability <= splash_probability:
            print('x_splash')
            return x_splash(genes, splash_count), len(genes[0]) + splash_count + int(splash_count / 2), True

    if max(players_x_dict.values()) / len(genes) > 0.6:
        probability = random.random()
        if probability <= splash_probability:
            print('y_splash')
            return y_splash(genes, splash_count), len(genes[0]) + splash_count + int(splash_count / 2), True
    return genes, len(genes[0]), False


def genetic_algorithm(initial_population_count, initial_length):
    next_population = get_initial_population(initial_population_count, initial_length)
    next_population_count = initial_population_count

    part_status = False
    must_eaten_goal_in_part = 1
    change_gene_from_index = 0

    best_fitness = 0
    best_fitness_count = 0
    best_fitness_count_limit = 10

    best_fitness_from_last_length_mutation = 0


    get_out_count = -3

    best_agent_movement = []
    best_agent_point = []


    for i in range(10000000000):
        game_list = run_whole_generation(next_population, next_population_count)

        goal_count = len(game_list.goal_player)

        if must_eaten_goal_in_part <= goal_count :
            part_status, good_gene_index = check_if_gene_is_good(game_list, must_eaten_goal_in_part)

        if part_status:
            must_eaten_goal_in_part +=1
            part_status = False
            change_gene_from_index = len(next_population[0])
            best_agent_point.append(0)
            best_agent_movement.append(next_population[good_gene_index])
            next_population = [next_population[good_gene_index] for i in range(initial_population_count)]
            next_population_count, new_length_mutated_genes = length_mutation(next_population, 1, 30)
            # change_gene_from_index += 15
            best_fitness = 0
            best_fitness_from_last_length_mutation = 0
            next_population = new_length_mutated_genes
            continue

        players_fitness = get_players_fitness(game_list)
        if None in players_fitness:
            best_agent_index = players_fitness.index(None)
            best_agent_point.append(new_players_fitness[best_agent_index])
            best_agent_movement.append(next_population[best_agent_index])
            return best_agent_movement, best_agent_point

        new_players_fitness = improve_lost_gene(game_list, players_fitness)

        if new_players_fitness:
            players_fitness = new_players_fitness
            best_agent_index = max(range(len(new_players_fitness)), key=new_players_fitness.__getitem__)
            best_agent_point.append(new_players_fitness[best_agent_index])
            best_agent_movement.append(next_population[best_agent_index])
            get_out_count = -3
        else:
            next_population = get_out_from_hell(next_population, get_out_count, change_gene_from_index)
            get_out_count -= 3
            best_fitness_count = 0

            if get_out_count < -1000:
                get_out_count = -3
                # next_population_count, new_length_mutated_genes = length_mutation(next_population, 1, 30)
                # next_population = new_length_mutated_genes
                next_population = mutation(selected_genes, change_gene_from_index, 1 / 2, int(len(next_population[0]) / 4))
            # if get_out_count == -45 :
            #     print("MOOM")
            #     next_population_count, new_length_mutated_genes = length_mutation(selected_genes, 1, 30)
            #     next_population = new_length_mutated_genes
            # next_population = mutation(next_population, len(next_population[0]) - 10, 1)
            continue

        selected_genes = selection(next_population, players_fitness)

        if max(players_fitness) > best_fitness:
            best_fitness = max(players_fitness)
            best_fitness_count = 0
        else:
            best_fitness_count += 1

        if best_fitness_count == best_fitness_count_limit:
            best_fitness_count = 0
            if best_fitness > best_fitness_from_last_length_mutation:
                best_fitness_from_last_length_mutation = best_fitness
                next_population_count, new_length_mutated_genes = length_mutation(selected_genes, 1)
                change_gene_from_index += 15
                next_population = new_length_mutated_genes
            else:
                # next_population, next_population_count, splash_status = splash(selected_genes, game_list)
                # if not splash_status:
                next_population = mutation(selected_genes, change_gene_from_index, 1/2, int(len(selected_genes[0])/4))
            continue

        next_population = cross_over(selected_genes, change_gene_from_index)
        # next_population = mutation(new_genes, change_gene_from_index)

# play_human_mode()
best_agent_movement, best_agent_point = genetic_algorithm(50,60)
#
# with open('best_agent_movement_map_2.txt', 'w') as f:
#     for item in best_agent_movement:
#         f.write("%s\n" % item)
#
# with open('best_agent_point_map_2.txt', 'w') as f:
#     for item in best_agent_point:
#         f.write("%s\n" % item)

# with open('best_agent_movement_map_2.txt') as file:
#     best_agent_movement = file.readlines()
#
#
# with open('best_agent_point_map_2.txt') as file:
#     best_agent_point = file.readlines()
#
# x = [i for i in range(len(best_agent_point))]
#
# plt.scatter(x=x, y=best_agent_point)
# plt.show()
#
# for movement in best_agent_movement:
#     play_game_AI(movement)
