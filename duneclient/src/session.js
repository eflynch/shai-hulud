import React from 'react';
import ReactDOM from 'react-dom';

import Board from './board';
import Faction from './faction';
import History from './history';

import Bidding from './rounds/bidding';
import Movement from './rounds/movement';


const getFactionOrder = (logoPositions, stormSector) => {
    const factionOrder = []
    for (let i=0; i<18; i++){
        const sector = (stormSector + i + 1) % 18
        logoPositions.forEach(([name, position]) => {
            if (position === sector) {
                factionOrder.push(name);
            }
        });
    }
    return factionOrder;
};


class Session extends React.Component {
    constructor(props) {
        super(props);
        this.state = {interaction: {
            mode: null
        }};
    }

    setInteraction = (interaction) => {
        this.setState({interaction: interaction});
    }
    getRoundState = (round_state) => {
        const {state, actions, history} = this.props;
        let stateDiv = null;
        let factionOrder = getFactionOrder(this.getLogoPositions(), state.storm_position);
        if (round_state && round_state.round == "bidding"){
            stateDiv = <Bidding factionOrder={factionOrder} roundstate={round_state} />;
        }
        if (round_state && round_state.round == "movement"){
            stateDiv = <Movement roundstate={round_state} />;
        }
        if (stateDiv === null){
            return <div className="roundstate">{JSON.stringify(round_state)}</div>;
        }
        return <div className="roundstate">{stateDiv}</div>;
    }

    getLogoPositions = () => {
        const {state, actions, history} = this.props;
        const fs = Object.keys(state.faction_state);
        return fs.map((faction) => {
            const factionstate = state.faction_state[faction];
            return [factionstate.name, factionstate.token_position];
        });
    }

    render () {
        const {state, actions, history, me} = this.props;
        const fs = Object.keys(state.faction_state).sort((x,y)=>{ return x == me ? -1 : y == me ? 1 : 0; });;

        const factions = fs.map((faction)=> {
            return <Faction key={faction} me={this.props.me} faction={faction} factionstate={state.faction_state[faction]}/>;
        });

        let futureStorm = undefined;
        if (state.storm_deck.next !== undefined) {
            futureStorm = (state.storm_deck.next + state.storm_position) % 18;
        }
        return (
            <div className="session">
                <div>
                    <Board me={this.props.me} interaction={this.state.interaction} setInteraction={this.setInteraction} logoPositions={this.getLogoPositions()}
                           stormSector={state.storm_position} futureStorm={futureStorm} state={state} />
                    {this.getRoundState(state.round_state)}
                </div>
                <History interaction={this.state.interaction} setInteraction={this.setInteraction} error={this.props.error} actions={actions} sendCommand={this.props.sendCommand} commandLog={history}/>
                <div className="factions">
                    {factions}
                </div>
            </div>
        );
    }
}


module.exports = Session;
