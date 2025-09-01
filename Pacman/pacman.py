import pygame
import time
from searchAgents import (
    MyBFSAgent, MyDFSAgent, MyUCSAgent,
    MyGreedyAgent, MyAStarAgent, MyIDDFSAgent,
    MyFoodBFSAgent, MyFoodDFSAgent, MyFoodUCSAgent,
    MyFoodGreedyAgent, MyFoodAStarAgent, MyFoodIDDFSAgent
)

from layouts import giantMaze ,smallMaze,mediumMaze,largeMaze,giantMaze_fewFood

CELL_SIZE = 30
FPS = 20

def draw_layout(screen, layout, pacman_pos, eaten, step, agent_name, agent_path):
    screen.fill((0,0,0))
    font = pygame.font.SysFont(None, 24)

    for i,row in enumerate(layout):
        for j,cell in enumerate(row):
            rect = pygame.Rect(j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if cell == "%":
                pygame.draw.rect(screen, (0,0,255), rect)
            elif cell == "." and (i,j) not in eaten:
                pygame.draw.circle(screen, (255,255,0), rect.center, CELL_SIZE//6)

    pacman_rect = pygame.Rect(pacman_pos[1]*CELL_SIZE, pacman_pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.circle(screen, (255,0,0), pacman_rect.center, CELL_SIZE//2)

    if step <= len(agent_path):
        next_move = agent_path[step-1]
        x,y = pacman_pos[1]*CELL_SIZE + CELL_SIZE//2, pacman_pos[0]*CELL_SIZE + CELL_SIZE//2
        dx, dy = 0,0
        if next_move == "Up": dy = -CELL_SIZE//2
        elif next_move == "Down": dy = CELL_SIZE//2
        elif next_move == "Left": dx = -CELL_SIZE//2
        elif next_move == "Right": dx = CELL_SIZE//2
        pygame.draw.line(screen, (255,0,0), (x,y), (x+dx,y+dy), 3)
        pygame.draw.circle(screen, (255,0,0), (x+dx,y+dy), 5)

    text = font.render(f"{agent_name} | Step: {step} | Comidas: {len(eaten)}", True, (255,255,255))
    screen.blit(text, (10,10))
    pygame.display.update()


def run_agent(agent_class, layout):
    agent = agent_class(layout)

    pacman_pos = None
    for i,row in enumerate(layout):
        for j,cell in enumerate(row):
            if cell == "." and " ":
                pacman_pos = (i,j)
                break
        if pacman_pos: break

    eaten = set()
    pygame.init()
    rows, cols = len(layout), len(layout[0])
    screen = pygame.display.set_mode((cols*CELL_SIZE, rows*CELL_SIZE+30))
    pygame.display.set_caption(agent_class.__name__)
    clock = pygame.time.Clock()

    # mover Pacman por la ruta final
    for step, move in enumerate(agent.path, start=1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        i,j = pacman_pos
        ni,nj = i,j
        if move == "Up": ni-=1
        elif move == "Down": ni+=1
        elif move == "Left": nj-=1
        elif move == "Right": nj+=1
        if 0<=ni<rows and 0<=nj<cols and layout[ni][nj] != "%":
            pacman_pos = (ni,nj)
        if layout[pacman_pos[0]][pacman_pos[1]] == "." and " ":
            eaten.add(pacman_pos)

        draw_layout(screen, layout, pacman_pos, eaten, step, agent_class.__name__, agent.path)
        clock.tick(FPS)

    time.sleep(1)
    pygame.quit()
    agent.report(agent_class.__name__)


if __name__ == "__main__":
    # ==============================
    # Agentes clásicos
    # ==============================
    print("=== Agentes clásicos ===")
    #run_agent(MyBFSAgent, giantMaze)
    #run_agent(MyDFSAgent, giantMaze)
    #run_agent(MyUCSAgent, giantMaze)
    #run_agent(MyGreedyAgent, giantMaze)
    #run_agent(MyAStarAgent, giantMaze)
    #run_agent(MyIDDFSAgent, giantMaze)

    # ==============================
    # Agentes Food Problem
    # ==============================
    print("=== Agentes Food Problem ===")
    run_agent(MyFoodBFSAgent, giantMaze_fewFood)
    run_agent(MyFoodDFSAgent, giantMaze_fewFood)
    run_agent(MyFoodUCSAgent, giantMaze_fewFood)
    run_agent(MyFoodGreedyAgent, giantMaze_fewFood)
    run_agent(MyFoodAStarAgent, giantMaze_fewFood)
    run_agent(MyFoodIDDFSAgent, giantMaze_fewFood)

