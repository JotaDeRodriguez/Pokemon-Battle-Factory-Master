# Pokémon Battle Factory Master

## Project Overview

This project aims to develop a set of AI agents that utilize Large Language Models integrated with complex frameworks and tool-calling to strategically defeat opponents in the Battle Factory mode in Pokémon Emerald. So far, similar challenges have been tackled using reinforcement learning, however the core of this project focuses on advanced planning and decision-making capabilities of LLMs to adapt to the varying challenges presented by this specific battle format.

## Why the Battle Factory

Pokemon Emerald's Battle Factory offers some unique challenges that differ from the main game. For starters, it offers a set selection of rental Pokemon, which limit the choices available to the player. In normal gameplay, the player is supposed to select the pokemon based on hints afforded to them before each battle. This limits the ammount of information the agents are expected to handle, while providing ample room for strategic approaches that will put the reasoning capabilities of the LLM agents to the test. Secondly, the battles go in a predictable format, with plenty of information available online to predict what's coming and hopefully let the agents decide a strategy that predicts the oponent's actions.


## Objectives and General Roadmap

So far, Im using a Prompt Template guided by a set of Json Files that provide info on the current pokemon on the field, as well as the available moves. This information gets passed over to another agent, who will build the strategic approach. So far, I'm focusing on testing the abilities of the agents to process the information. Giving them the ability to actually call on the moves themselves on an emulator will depend on the results, and will come later down the road.


## Contributing

Im interested in collaborations and suggestions! This is one of my very first projects with agents and it's a testing ground for approaches that ensure LLMs are able to understand and act according to precise information, and provide accurate results. My inbox is open to anyone wanting to contribute or have a chat about this.

## License

[MIT](https://choosealicense.com/licenses/mit/),  see the LICENSE.md file for details.
