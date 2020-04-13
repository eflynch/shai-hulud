import React from 'react';

import TokenPile from './components/token-pile';
import Spice from './components/spice';
import Card from './components/card';
import LeaderToken from './components/leader-token';
import update from 'immutability-helper';


class Faction extends React.Component {
    getTreachery () {
        if (!this.props.factionstate.hasOwnProperty("treachery")){
            return [];
        }

        if (Array.isArray(this.props.factionstate.treachery)){
            return this.props.factionstate.treachery.map((name, i) => {
                return <Card type="Treachery" key={i} name={name}/>;
            });
        } else {
            let treachery = [];
            for (let i=0; i < this.props.factionstate.treachery.length; i++){
                treachery.push(<Card type="Treachery" key={"reverse-"+i} name="Reverse" />);
            }
            return treachery;
        }
    }
    getLeaders () {
        const allLeaders = this.props.factionstate.leaders.concat(this.props.factionstate.tank_leaders);
        if (this.props.faction == "atreides" &&
            this.props.factionstate.kwisatz_haderach_available) {
            allLeaders.push(["Kwisatz-Haderach", 2]);
        }
        return (
            <div style={{display:"flex", flexWrap:"wrap"}}>
                {allLeaders.map((leader) => {
                    let dead = false;
                    if (this.props.factionstate.tank_leaders.indexOf(leader) !== -1){
                        dead = true;
                    }
                    if (leader[0] == "Kwisatz-Haderach" && this.props.factionstate.kwisatz_haderach_tanks != null) {
                        dead = true;
                    }
                    const leaderName = leader[0];
                    return <LeaderToken
                            key={"leader-"+leaderName}
                            name={leaderName}
                            dead={dead}/>;
                })}
            </div>
        );
    }
    getTraitors () {
        if (this.props.me !== this.props.faction){
            return [];
        }
        return this.props.factionstate.traitors.map((traitor) => {
            const traitorName = traitor[0];
            return <Card type="Traitor"
                    key={"traitor-"+traitorName}
                    name={traitor[0]}/>;
        });
    }
    getTokens () {
        let number = this.props.factionstate.reserve_units.length;
        let power = this.props.factionstate.reserve_units.reduce((a, b) => a + b, 0);
        return <TokenPile width={50} faction={this.props.faction} number={number} bonus={power-number}/>
    }
    getSpice () {
        if (this.props.factionstate.spice !== undefined){
            return (
                <div style={{display: "flex", flexDirection: "column", alignItems:"center"}}>
                    Spice<Spice width={75} amount={this.props.factionstate.spice}/>
                </div>
            );
        }
        return <div/>;
    }
    getBribeSpice () {
        if (this.props.factionstate.bribe_spice !== undefined){
            return (
                <div style={{display: "flex", flexDirection: "column", alignItems:"center"}}>
                    Bribe<Spice width={75} amount={this.props.factionstate.bribe_spice}/>
                </div>
            );
        }
        return <div/>;
    }
    render () {
        return (
            <div className={"faction" + (this.props.me === this.props.faction ? " me" : "")}>
                <h2>{this.props.faction}</h2>
                {this.getLeaders()}
                {this.getTokens()}
                {this.getSpice()}
                <div style={{display:"flex", flexWrap: "wrap"}}>
                    {this.getTreachery()}
                    {this.getTraitors()}
                </div>
                {this.getBribeSpice()}
            </div>
        );
    }
}

module.exports = Faction;
