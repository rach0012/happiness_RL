# Python imports.
from __future__ import print_function
import sys
import time
import random
try:
    import pygame
    from pygame.locals import *
    pygame.init()
    title_font = pygame.font.SysFont("CMU Serif", 48)
except ImportError:
    print("Error: pygame not installed (needed for visuals).")
    exit()

def val_to_color(val, good_col=(94, 142, 253), bad_col=(249, 193, 169)):
    '''
    Args:
        val (float)
        good_col (tuple)
        bad_col (tuple)

    Returns:
        (tuple)

    Summary:
        Smoothly interpolates between @good_col and @bad_col. That is,
        if @val is 1, we get good_col, if it's 0.5, we get a color
        halfway between the two, and so on.
    '''
    # Make sure val is in the appropriate range.
    val = max(min(1.0, val), -1.0)

    if val > 0:
        # Show positive as interpolated between white (0) and good_cal (1.0)
        result = tuple([255 * (1 - val) + (col * val) for col in good_col])
    else:
        # Show negative as interpolated between white (0) and bad_col (-1.0)
        result = tuple([255 * (1 - abs(val)) + (col * abs(val)) for col in bad_col])

    return result

def count_to_color(val, good_col=(169, 193, 249), bad_col=(249, 193, 169)):
    '''
    Args:
        val (float)
        good_col (tuple)
        bad_col (tuple)

    Returns:
        (tuple)

    Summary:
        Smoothly interpolates between @good_col and @bad_col. That is,
        if @val is 500, we get good_col, if it's 250, we get a color
        halfway between the two, and so on.
    '''
    # Make sure val is in the appropriate range.
    val = val/100 #to fix this, hard-coded
    val = max(min(1.0, val), -1.0)
    if val > 0:
        # Show positive as interpolated between white (0) and good_cal (1.0)
        result = tuple([255 * (1 - val) + (col * val) for col in good_col])
    else:
        # Show negative as interpolated between white (0) and bad_col (-1.0)
        result = tuple([255 * (1 - abs(val)) + (col * abs(val)) for col in bad_col])

    return result

def _draw_title_text(mdp, screen):
    '''
    Args:
        mdp (simple_rl.MDP)
        screen (pygame.Surface)

    Summary:
        Draws the name of the MDP to the top of the screen.
    '''
    scr_width, scr_height = screen.get_width(), screen.get_height()
    title_text = title_font.render(str(mdp), True, (46, 49, 49))
    screen.blit(title_text, (scr_width / 2.0 - len(str(mdp))*6, scr_width / 20.0))

def _draw_agent_text(agent, screen):
    '''
    Args:
        agent (simple_rl.Agent)
        screen (pygame.Surface)

    Summary:
        Draws the name of the agent to the bottom right of the screen.
    '''
    scr_width, scr_height = screen.get_width(), screen.get_height()
    formatted_agent_text = "agent: " + str(agent)
    agent_text_point = (3*scr_width / 4.0 - len(formatted_agent_text)*6, 18*scr_height / 20.0)
    agent_text = title_font.render(formatted_agent_text, True, (46, 49, 49))
    screen.blit(agent_text, agent_text_point)

def _draw_lower_left_text(state, screen, score=-1):
    '''
    Args:
        state (simple_rl.State)
        screen (pygame.Surface)
        score (int)

    Summary:
        Draws the name of the current state to the bottom left of the screen.
    '''
    scr_width, scr_height = screen.get_width(), screen.get_height()
    # Clear.
    formatted_state_text = str(state) if score == -1 else score
    if len(formatted_state_text) > 20:
        # State text is too long, ignore.
        return
    state_text_point = (scr_width / 4.0 - len(formatted_state_text)*7, 18*scr_height / 20.0)
    pygame.draw.rect(screen, (255,255,255), (state_text_point[0] - 20, state_text_point[1]) + (200,40))
    state_text = title_font.render(formatted_state_text, True, (46, 49, 49))
    screen.blit(state_text, state_text_point)

def visualize_policy(mdp, agent, draw_state, step, cur_state=None, scr_width=1200, scr_height=1200, 
    folder='results/'):
    screen = pygame.display.set_mode((scr_width, scr_height))
    cur_state = mdp.get_init_state() if cur_state is None else cur_state

    agent_shape = _vis_init(screen, mdp, draw_state, cur_state, steps=step, agent=agent, value=False)
    draw_state(screen, mdp, cur_state, policy=agent.policy, action_char_dict={},
        show_value=False, draw_statics=True, agent=agent, agent_shape=agent_shape)

    pygame.image.save(screen, folder+"policies_"+str(step)+".jpeg")
    pygame.display.flip()

def visualize_value(mdp, agent, draw_state, step, cur_state=None, scr_width=1200, scr_height=1200, 
    folder='results/'):
    '''
    Args:
        mdp (MDP)
        draw_state (State)

    Summary:
        Draws the MDP with values labeled on states.
    '''

    screen = pygame.display.set_mode((scr_width, scr_height))
    cur_state = mdp.get_init_state() if cur_state is None else cur_state

    agent_shape = _vis_init(screen, mdp, draw_state, cur_state, agent=agent, steps=step, value=True)
    draw_state(screen, mdp, cur_state, show_value=True, draw_statics=True, agent=agent, agent_shape=agent_shape)
    pygame.image.save(screen, folder+"values_"+str(step)+".jpeg")
    pygame.display.flip()
    
def visualize_counts(mdp, agent, draw_state, draw_state_2, visit_counts, step, 
    cur_state=None, scr_width=1200, scr_height=1200, folder='results/'):
    '''
    Args:
        mdp (MDP)
        agent (Agent)
        draw_state (lambda: State --> pygame.Rect)
        visit_counts (visit counts of the state)
        cur_state (State)
        scr_width (int)
        scr_height (int)
        step(int) how many steps were taken before calling this visualize method (for image saving)

    Summary:
        Creates a 2d visual of the visit counts of the different states
    '''
    screen = pygame.display.set_mode((scr_width, scr_height))

    # Setup and draw initial state.
    cur_state = mdp.get_init_state()
    agent_shape = _vis_init(screen, mdp, draw_state, cur_state, agent=agent, steps=step)
    draw_state_2(screen, mdp, cur_state, visit_counts, agent=agent, 
        show_value=True, draw_statics=True, agent_shape=agent_shape)
    pygame.image.save(screen, folder+"counts_"+str(step)+".jpeg")
    done = False
    pygame.display.flip()

def visualize_learning(mdp, agent, draw_state, cur_state=None, 
    scr_width=800, scr_height=800, delay=0, num_ep=None, num_steps=None, 
    counterfactual_state=None, non_stationary = True, frequency_change = 4):
    '''
    Args:
        mdp (MDP)
        agent (Agent)
        draw_state (lambda: State --> pygame.Rect)
        cur_state (State)
        scr_width (int)
        scr_height (int)
        delay (float): seconds to add in between actions.

    Summary:
        Creates a *live* 2d visual of the agent's
        interactions with the MDP, showing the agent's
        estimated values of each state.
    '''
    screen = pygame.display.set_mode((scr_width, scr_height))
    #print(mdp.get_goal_locs())
    # Setup and draw initial state.
    cur_state = mdp.get_init_state() if cur_state is None else cur_state
    reward = 0
    rpl = 0 
    score = 0
    counterfactual_reward = 0
    counterfactual_state = mdp.get_init_state() if counterfactual_state is None else counterfactual_state
    counterfactual_regret = True #change here
    
    default_goal_x, default_goal_y = mdp.width, mdp.height
    agent_shape = _vis_init(screen, mdp, draw_state, cur_state, agent=agent, score=score)
    
    pygame.display.update()
    done = False

    counter = 0
    if not num_ep:
        # Main loop.
        while not done:
            # Check for key presses.
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    # Quit.
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_r:
                    score = 0
                    agent.reset()
                    mdp.goal_locs = [(default_goal_x, default_goal_y)]
                    mdp.reset()

                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    x, y = pos[0], pos[1]
                    width_buffer = scr_width / 10.0
                    height_buffer = 30 + (scr_height / 10.0) # Add 30 for title.
                    cell_x, cell_y = convert_x_y_to_grid_cell(x, y, scr_width, scr_height, mdp.width, mdp.height)

                    if event.button == 1:
                        # Left clicked a cell, move the goal.
                        mdp.goal_locs = [(cell_x, cell_y)]
                        mdp.reset()
                    elif event.button == 3:
                        # Right clicked a cell, move the lava location.
                        if (cell_x, cell_y) in mdp.lava_locs:
                            mdp.lava_locs.remove((cell_x, cell_y))
                        else:
                            mdp.lava_locs += [(cell_x, cell_y)]

            counter += counter                
            # Move agent.
            if counterfactual_regret:
                action, happiness = agent.act(cur_state, reward, counterfactual_state, counterfactual_reward, score, counter) #for happy q-learning
            else:
                action, happiness = agent.act(cur_state, reward, score, counter)#for all other agents
                
            if counterfactual_regret:
                counter_action = agent.counterfactual_policy(action) #obtain the counterfactual action by a random agent

            if cur_state.is_terminal():
                score += 1
                cur_state = mdp.get_init_state()
                mdp.reset()
                agent.end_of_episode()
                agent_shape = _vis_init(screen, mdp, draw_state, cur_state, agent=agent, score=score)
            
            
            #this will serve as counterfactual state and reward in next round
            counterfactual_reward, counterfactual_state  = mdp.simulate_agent_action(counter_action) 
            reward, cur_state = mdp.execute_agent_action(action)            
            
            agent_shape = draw_state(screen, mdp, cur_state, agent=agent, show_value=True, draw_statics=True,agent_shape=agent_shape)

            score += int(reward)

            pygame.display.update()

            time.sleep(delay)

    else:
        # Main loop.
        i = 0
        
        index1 = 0 #for changing goal locations, as of now, goal locations fluctate between the 4 corners
        index2 = 0
        positions1 = [(1,1), (7,1)]
        positions2 = [(1,7), (7,7)]
        
        while i < num_ep:
            j = 0
            g = mdp.get_goal_locs() #original goal location
            c = 0   
            while j < num_steps:
                # Check for key presses.
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        # Quit.
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN and event.key == K_r:                        
                        score = 0
                        agent.reset()
                        mdp.goal_locs = [(default_goal_x, default_goal_y)]
                        mdp.reset()
                        
                #if non-stationary, and steps matches frequency_change, then change the goal location of the mdp  
                a = list(range(int(num_steps/frequency_change), int(num_steps+1), int(num_steps/frequency_change)))    
                
                if non_stationary:
                    if j in a: 
                        #print(c,g, mdp.goal_locs)
                        if c == 0:
                            c = 1
                            if index1 >= len(positions1): #if gone over, then cyce through list again
                                   index1 = 0
                            mdp.goal_locs = [positions1[index1]] #to fix, make this non-hard coded 
                            index1 = index1+1                     
                        elif c == 1:                            
                            c = 0
                            if index2 >= len(positions2): #if gone over, then cyce through list again
                                   index2 = 0
                            mdp.goal_locs = [positions2[index2]] #to fix, make this non-hard coded 
                            index2 = index2+1

                # Move agent.
                if counterfactual_regret:
                    action, happiness = agent.act(cur_state, reward, counterfactual_state, counterfactual_reward, score, j) #for happy q-learning
                else:
                    action, happiness = agent.act(cur_state, reward, score, j)#for all other agents
                
                if counterfactual_regret:
                    counter_action = agent.counterfactual_policy(action) #obtain the counterfactual action by a random agent
                
                #this will serve as counterfactual state and reward in next round
                counterfactual_reward, counterfactual_state = mdp.simulate_agent_action(counter_action) 
                
                reward, cur_state = mdp.execute_agent_action(action)
                
                agent_shape = draw_state(screen, mdp, cur_state, agent=agent, show_value=True, draw_statics=True,agent_shape=agent_shape)
                
                score = round(rpl)
                rpl += reward

                pygame.display.update()

                time.sleep(delay)
                j+=1

                if cur_state.is_terminal():
                    cur_state = mdp.get_init_state()
                    mdp.reset()
                    agent_shape = _vis_init(screen, mdp, draw_state, cur_state, agent=agent, score=score)
                    break
            
            i+=1
            cur_state = mdp.get_init_state()
            mdp.reset()
            agent_shape = _vis_init(screen, mdp, draw_state, cur_state, agent=agent, score=score)
                    
            draw_state(screen, mdp, cur_state, policy=agent.policy, action_char_dict={}, 
            	show_value=False, agent=agent, draw_statics=True)
    pygame.display.flip()


def visualize_agent(mdp, agent, draw_state, cur_state=None, scr_width=1500, scr_height=1500):
    '''
    Args:
        mdp (MDP)
        agent (Agent)
        draw_state (lambda: State --> pygame.Rect)
        cur_state (State)
        scr_width (int)
        scr_height (int)

    Summary:
        Creates a 2d visual of the agent's interactions with the MDP.
    '''
    screen = pygame.display.set_mode((scr_width, scr_height))

    # Setup and draw initial state.
    cur_state = mdp.get_init_state() if cur_state is None else cur_state
    reward = 0
    agent_shape = _vis_init(screen, mdp, draw_state, cur_state, agent)

    done = False
    while not done:

        # Check for key presses.
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                # Quit.
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_SPACE:
                # Move agent.
                action, happiness = agent.act(cur_state, reward)
                reward, cur_state = mdp.execute_agent_action(action)
                agent_shape = draw_state(screen, mdp, cur_state, agent_shape=agent_shape)

                # Update state text.
                _draw_lower_left_text(cur_state, screen)

        if cur_state.is_terminal():
            # Done! Agent found goal.
            goal_text = "Victory!"
            goal_text_rendered = title_font.render(goal_text, True, (206, 147, 66))
            goal_text_point = scr_width / 2.0 - (len(goal_text)*7), 18*scr_height / 20.0
            screen.blit(goal_text_rendered, goal_text_point)
            done = True

        pygame.display.flip()

def visualize_interaction(mdp, draw_state, cur_state=None, scr_width=720, scr_height=720):
    '''
    Args:
        mdp (MDP)
        draw_state (lambda: State --> pygame.Rect)

    Summary:
        Creates a 2d visual of the agent's interactions with the MDP.
    '''
    screen = pygame.display.set_mode((scr_width, scr_height))

    from simple_rl.agents import RandomAgent
    agent = RandomAgent

    # Setup and draw initial state.
    cur_state = mdp.get_init_state() if cur_state is None else cur_state
    reward = 0
    agent_shape = _vis_init(screen, mdp, draw_state, cur_state, agent)

    actions = mdp.get_actions()

    keys = [K_1, K_2, K_3, K_4, K_5, K_6]
    keys = keys[:len(actions)]

    done = False
    while not done:

        # Check for key presses.
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                # Quit.
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key in keys:
                action = actions[keys.index(event.key)]
                reward, cur_state = mdp.execute_agent_action(action=action)
                agent_shape = draw_state(screen, mdp, cur_state, agent_shape=agent_shape)

                # Update state text.
                _draw_lower_left_text(cur_state, screen)

        if cur_state.is_terminal():
            # Done! Agent found goal. Not if the state is lava!! (Tofix)
            goal_text = "Victory!"
            goal_text_rendered = title_font.render(goal_text, True, (246, 207, 106))
            goal_text_point = scr_width / 2.0 - (len(goal_text)*7), 18*scr_height / 20.0
            screen.blit(goal_text_rendered, goal_text_point)
            done = True

        pygame.display.update()

def _vis_init(screen, mdp, draw_state, cur_state, steps=0, agent=None, value=False, score=-1):
    # Pygame setup.
    pygame.init()
    screen.fill((255, 255, 255))
    pygame.display.update()
    done = False

    if score != -1:
        _draw_lower_left_text("Score: " + str(score), screen)

    #also show steps taken so far    
    if steps > 0:
        scr_width, scr_height = screen.get_width(), screen.get_height()
        title_text = title_font.render('steps: '+str(steps), True, (46, 49, 49))
        screen.blit(title_text, (scr_width / 2.5 - len(str(steps))*6, scr_width / 20.0))    
        
    agent_shape = draw_state(screen, mdp, cur_state, agent=agent, show_value=value, draw_statics=True)

    return agent_shape

def convert_x_y_to_grid_cell(x, y, scr_width, scr_height, mdp_width, mdp_height):
    '''
    Args:
        x (int)
        y (int)
        scr_width (int)
        scr_height (int)
        num
    '''
    width_buffer = scr_width / 10.0
    height_buffer = 30 + (scr_height / 10.0) # Add 30 for title.

    lower_left_x, lower_left_y = x - width_buffer, scr_height - y - height_buffer
    
    cell_width = (scr_width - width_buffer * 2) / mdp_width
    cell_height = (scr_height - height_buffer * 2) / mdp_height

    cell_x, cell_y = int(lower_left_x / cell_width) + 1, int(lower_left_y / cell_height) + 1

    return cell_x, cell_y




