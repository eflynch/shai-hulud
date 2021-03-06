import React, {useState} from 'react';
import Slider, { Range } from 'rc-slider';
import update from 'immutability-helper';

import BattlePlan, {PlanLeader, PlanNumber, PlanTreachery} from './widgets/battle-plan';
import TraitorSelect from './widgets/traitor-select';
import Integer from './widgets/integer';
import Units from './widgets/units';
import Card from './components/card';
import Logo from './components/logo';


const humanReadable = {
    "token-select": "Token Placement",
    "space-sector-select-start": "From",
    "space-sector-select-end": "To",
    "traitor-select": "Traitor",
    "leader-input": "Leader",
    "space-select": "Space",
};

const Options = ({args, setArgs, options}) => {
    return (
        <div style={{display:"flex", justifyContent:"space-evenly", flexWrap: "wrap", maxWidth:400}}>
            {options.map((option)=> {
                return <div key={option} className={"option" + (option === args ? " selected": "")} onClick={()=>{
                    setArgs(option);
                }}>{option}</div>;
            })}
        </div>
    );
};


const PrescienceAnswer = ({me, state, args, setArgs, maxPower}) => {
    const stageState = state.round_state.stage_state;
    const query = stageState.prescience;
    if (query === "leader") {
        const fs = state.faction_state[me];
        return <PlanLeader leaders={fs.leaders} treachery={fs.treachery} selectedLeader={args} setLeader={setArgs} active={true} />;
    } else if (query === "number") {
        const [space, sector] = stageState.battle.slice(2);
        return <PlanNumber maxNumber={maxPower} number={parseInt(args)} setNumber={(number)=>{
            setArgs("" +number);
        }} active={true} />;
    } else if (query === "weapon") {
        const meWeapons = state.faction_state[me].treachery.filter(
            (t)=>state.treachery_reference.weapons.indexOf(t) !== -1);
        return <PlanTreachery title="Weapon" cards={meWeapons} selectedCard={args} setSelectedCard={setArgs} active={true} />;
    } else if (query === "defense") {
        const meDefenses = state.faction_state[me].treachery.filter(
            (t)=>state.treachery_reference.defenses.indexOf(t) !== -1);
        return <PlanTreachery title="Defense" cards={meDefenses} selectedCard={args} setSelectedCard={setArgs} active={true} />;
    }
};


const UnitSelect = ({value, selected, active, setSelected}) => {
    return <div style={{
        cursor:"pointer",
        width: 20,
        height: 20,
        border: "1px solid black",
        borderRadius: 10,
        backgroundColor: selected ? "red" : "white",
        opacity: selected || active ? 1 : 0.2,
        color: selected? "white" : "black",
        userSelect: "none",
    }} onClick={()=>{
        if (selected) {setSelected(false);}
        else if (active){setSelected(true);}
    }}>{value}</div>;
}

const UnitPicker = ({available, selected, setSelected, canAddMore}) => {
  const unitSelectors = []
  for (const type of Object.keys(available)) {
    for (const index of Array(available[type]).keys()) {
      const isSelected = selected[type] && index < selected[type];
      unitSelectors.push(<UnitSelect
           key={`${type}-${index}`}
           value={type}
           active={isSelected || canAddMore}
           selected={isSelected}
           setSelected={(s)=>{
             setSelected(update(selected, {[type]: {$set: selected[type] + (s ? 1 : -1)}}));
           }}
          />);
    }
  }
  return <div style={{display:"flex"}}>{unitSelectors}</div>;
};

const TankUnits = ({me, state, args, setArgs}) => {
    const selectedUnits = {};
    let totalSelected = 0;
    if (args !== "") {
        args.split(" ").forEach((a)=>{
            const [sector, units] = a.split(":");
            const unitsParsed = units.split(",").map((i)=>parseInt(i));
            const numOnes = unitsParsed.filter((i)=>i===1).length;
            const numTwos = unitsParsed.filter((i)=>i===2).length;
            selectedUnits[sector] = {
                1: numOnes,
                2: numTwos
            };
            totalSelected += numOnes + (2*numTwos);
        });
    }


    const [attacker, defender, space, sector] = state.round_state.stage_state.battle;
    const forces = state.map_state.filter(s=>s.name === space)[0].forces[me];
    const sectors = Object.keys(forces);

    sectors.forEach((sector)=> {
        if (selectedUnits[sector] === undefined) {
            selectedUnits[sector] = {1: 0, 2: 0};
        }
    });


    const toTank = me === attacker ? state.round_state.stage_state.attacker_plan.number : state.round_state.stage_state.defender_plan.number;
    const active = totalSelected < toTank;

    const _formatArgs = (selectedUnits) => {
        const sectors = Object.keys(selectedUnits);
        return sectors.map((s)=>{
            return `${s}:${Array(selectedUnits[s][1]).fill("1").concat(Array(selectedUnits[s][2]).fill("2")).join(",")}`;
        }).join(" ");
    };

    return (
        <div>
            <div style={{textAlign: "left"}}><span>Select {toTank - totalSelected} more power:</span></div>
            {sectors.map((sector)=>{
                const availableForcesFlat = forces[sector].slice().sort();
                const availableForces = {};
                for (const force of availableForcesFlat) {
                  if (!availableForces[force]) {
                    availableForces[force] = 1;
                  } else {
                    availableForces[force] += 1;
                  }
                }
                const selectedForces = selectedUnits[sector];
                return (
                    <div key={"sector" + sector} style={{display:"flex", alignItems:"center", justifyContent:"space-between"}}>
                        <span>Sector {sector}:</span>
                        <UnitPicker selected={selectedForces}
                                    available={availableForces}
                                    canAddMore={active}
                                    setSelected={(newSelected) => {
                                      setArgs(_formatArgs(update(selectedUnits, {[sector]: {$set: newSelected}})));
                                    }}
                        />
                    </div>
                );
            })}
        </div>
    );
};

const DiscardTreachery = ({state, me, args, setArgs}) => {
    let weaponSelected = false;
    let defenseSelected = false;
    if (args !== "") {
        weaponSelected = args.split(" ").indexOf("weapon") !== -1;
        defenseSelected = args.split(" ").indexOf("defense") !== -1;
    }
    const [attacker, defender, space, sector] = state.round_state.stage_state.battle;
    const weapon = me === attacker ? state.round_state.stage_state.attacker_plan.weapon : state.round_state.stage_state.defender_plan.weapon;
    const defense = me === attacker ? state.round_state.stage_state.attacker_plan.defense : state.round_state.stage_state.defender_plan.defense;

    const _option = (maybeCard, selected, kind) => {
        if (maybeCard) {
            return <Card type="Treachery" name={maybeCard} selected={selected} width={100} onClick={()=>{
                if (kind === "weapon"){
                    setArgs([!weaponSelected ? "weapon" : "", defenseSelected ? "defense" : ""].join(" "))
                } else {
                    setArgs([weaponSelected ? "weapon" : "", !defenseSelected ? "defense" : ""].join(" "))
                }
            }}/>;
        }
    }
    return (
        <div style={{display:"flex"}}>
            {_option(weapon, weaponSelected, "weapon")}
            {_option(defense, defenseSelected, "defense")}
        </div>
    );
};


const ReturnTreachery = ({state, me, args, setArgs, number}) => {
    const selectedCards = args ? args.split(" ") : [];
    const numSelected = selectedCards.length;
    const treachery = state.faction_state[me].treachery;

    return (
        <div style={{display:"flex"}}>
            {treachery.map((card, i)=> {
                const selected = selectedCards.indexOf(card) !== -1;
                return <Card key={card + i} type="Treachery" name={card} selected={selected} width={100} onClick={()=>{
                    if (selected) {
                        const index = selectedCards.indexOf(card)
                        selectedCards.splice(index, 1);
                        setArgs(selectedCards.join(" "));
                    } else {
                        if (numSelected < number) {
                            selectedCards.push(card)
                            setArgs(selectedCards.join(" "));
                        }
                    }
                }
                }/>;
            })}
        </div>
    );
};
 
const Choice = ({args, setArgs, clearSelection, config, ...props}) => {
    return (
        <div>
            {config.map((subWidget, i) => {
                return (
                    <div key={i}>
                        <Widget {...props} key={i} type={subWidget.widget} config={subWidget.args} args={args} setArgs={(args) => {
                            clearSelection();
                            setArgs(args);
                        }} clearSelection={clearSelection}/>
                    </div>
                );
            })}
        </div>
    );
};

const Struct = ({args, setArgs, config, ...props}) => {
    return (
        <div>
            {config.map((subWidget, i) => {
                return <Widget {...props} key={i} type={subWidget.widget} config={subWidget.args} setArgs={(subArgs)=> {
                    setArgs((args) => {
                        return update(args, {[i]: {$set: subArgs}});
                    });
                }} args={args[i]} />
            })}
        </div>
    );
};

const ArrayWidget = ({args, setArgs, config, ...props}) => {
    const subArgs = args.split(":");
    let widgets = subArgs.map((arg, i) => {
        return <Widget {...props} key={i} type={config.widget} config={config.args} args={arg} setArgs={(args)=> {
            setArgs(update(subArgs, {[i]: {$set: args}}).join(":"));
        }} args={subArgs[i]} />;
    });

    return (
        <div>
            {widgets}
            <button onClick={(e)=>{setArgs(args + ":")}} >+</button>
        </div>
    );
};

const Input = ({args, setArgs, config}) => {
    return <input value={args} onChange={((e)=>{
        const value = e.target.value;
        setArgs(value);
    })}/>;
};

const Constant = ({value, setArgs}) => {
    return <button onClick={()=>{setArgs(value);}}>{value}</button>;
}


const SelectOnMap = ({args, setArgs, interaction, setInteraction, mode, nullable, updateSelection}) => {
    const setAndSelectArgs = (newArgs) => {
        updateSelection(mode, newArgs);
        setArgs(newArgs);
    };

    let pieces = [
            <div key="select" className={"select-on-map" + (mode === interaction.mode ? " on" : " off")} onClick={(e)=>{
                setAndSelectArgs("");
                setInteraction({
                        mode,
                        action: (val) => {
                            setAndSelectArgs(val);
                        },
                });
            }}>Select on Board</div>,
    ];
    if (args && args !== "-") {
        pieces.push(<div key="value">Selected: {args}</div>);
    }
    if (nullable) {
        pieces.push(<div onClick={(e)=>{
            setArgs("");
        }}>x</div>);
    }
    return (
        <div style={{display:"flex", flexDirection: "column", alignItems:"center"}}>
            <span>{(mode in humanReadable) ? humanReadable[mode] : mode}:</span>
            {pieces}
        </div>
    );
};



const FactionSelector = ({faction, selected, diameter, onSelect}) => {
    return (
        <Logo className={"select-faction" + (selected ? " selected" : "")} onClick={onSelect} faction={faction} diameter={diameter} />
    );
}

const FactionSelect = ({args, setArgs, factionsAvailable, allowMulti}) => {
    const selectedFactions = args ? args.split(" ") : [];
    return (
        <div style={{display:"flex", justifyContent:"space-around", flexWrap:"wrap"}}>
            {factionsAvailable.map((faction)=> {
                const selected = selectedFactions.indexOf(faction) !== -1;
                return <FactionSelector diameter={75} key={faction} faction={faction} selected={selected} onSelect={()=>{
                    if (allowMulti) {
                        if (selected) {
                            setArgs(selectedFactions.filter(f => f !== faction).join(" "));
                        } else {
                            selectedFactions.push(faction);
                            setArgs(selectedFactions.join(" "));
                        }
                    } else {
                        setArgs(selected ? "" : faction);
                    }
                }} />;
            })}
        </div>
    );
};

const FremenPlacementSelect = ({args, setArgs, config}) => {
    const [tabr, west, south, westSector, southSector] = args.split(":");
    return (
        <div>
            <h3>Sietch Tabr</h3>
            <Units args={tabr} setArgs={(args)=>{
                setArgs([args, west, south, westSector, southSector].join(":"));
            }} fedaykin={true} />
            <h3>False Wall West</h3>
            <Units args={west} setArgs={(args)=>{
                setArgs([tabr, args, south, westSector, southSector].join(":"));
            }} fedaykin={true} />
            Sector:
            <Integer min={15} max={17} args={westSector} setArgs={(args)=>{
                setArgs([tabr, west, south, args, southSector].join(":"));
            }}/>
            <h3>False Wall South</h3>
            <Units args={south} setArgs={(args)=>{
                setArgs([tabr, west, args, westSector, southSector].join(":"));
            }} fedaykin={true} />
            Sector:
            <Integer min={3} max={4} args={southSector} setArgs={(args)=>{
                setArgs([tabr, west, south, westSector, args].join(":"));
            }}/>
        </div>
    );
};

const RevivalLeader = ({me, args, leaders, setArgs, required}) => {
    return <PlanLeader leaders={leaders} treachery={[]} selectedLeader={args} setLeader={(leader)=>{
        if (leader) {
            setArgs(leader);
        } else {
            setArgs('-');
        }
    }} active={true} canDeselect={!required}/>;
};

const RevivalUnits = ({me, args, setArgs, units, maxUnits, single2, title}) => {
    const unitArgs = title ? (args ? args.split(" ")[1] : "") : args;
    const hasUnitsSelected = (unitArgs.indexOf("1") !== -1) || (unitArgs.indexOf("2") !== -1);
    const unitsSelected = hasUnitsSelected ? unitArgs.split(",").map((u)=>parseInt(u)).filter((u)=>u) : [];
    const selectedUnits = {
      1: unitsSelected.filter((u)=>u==1).length,
      2: unitsSelected.filter((u)=>u==2).length,
    };

    const numTwosAvailable = (() => {
        const numTwosAvailable = Math.min(units.filter((u)=>u==2).length, maxUnits);
        if (single2 && numTwosAvailable) {
             return 1;
        }
        return numTwosAvailable;
    })();

    const numOnesAvailable = Math.min(units.filter((u)=>u==1).length, maxUnits);
    const availableUnits = {
      1: numOnesAvailable,
      2: numTwosAvailable,
    };
    const active = unitsSelected.length < maxUnits;

    return <UnitPicker available={availableUnits}
                       selected={selectedUnits}
                       setSelected={(newSelected) => {
                         const newSelectedString = `${Array(newSelected[1]).fill("1").concat(Array(newSelected[2]).fill("2")).join(",")}`;
                         if (title) {
                           setArgs([title, newSelectedString].join(" "));
                         } else {
                           setArgs(newSelectedString);
                         }
                       }}
                       canAddMore={active}/>;
};


const Widget = (props) => {
    const {me, state, type, args, config, interaction, setInteraction, clearSelection, updateSelection, setArgs} = props;

    if (type === "null") {
        return "";
    }

    if (type === "choice") {
        return <Choice state={state} me={me} args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction} updateSelection={updateSelection} clearSelection={clearSelection}/>; 
    }

    if (type === "struct") {
        return <Struct state={state} me={me} args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction} updateSelection={updateSelection} clearSelection={clearSelection}/>; 
    }

    if (type === "input") {
        return <Input args={args} setArgs={setArgs} config={config} updateSelection/>; 
    }

    if (type === "faction-select") {
        const factionsAvailable = Object.keys(state.faction_state).filter(f => f !== me);
        return <FactionSelect allowMulti={false} factionsAvailable={factionsAvailable} args={args} setArgs={setArgs} />;
    }

    if (type === "multi-faction-select") {
        return <FactionSelect allowMulti={true} factionsAvailable={config.factions} args={args} setArgs={setArgs} />;
    }


    if (type === "constant") {
        return <Constant value={config} setArgs={setArgs} />;
    }

    if (type === "units") {
        return <Units args={args} setArgs={setArgs} fedaykin={config.fedaykin} sardaukar={config.sardaukar}/>;
    }

    if (type === "token-select") {
        return <SelectOnMap mode="token-select" interaction={interaction} setInteraction={setInteraction} setArgs={setArgs} updateSelection={updateSelection} args={args} />;
    }

    if (type === "array") {
        return <ArrayWidget args={args} setArgs={setArgs} config={config} state={state} me={me} />;
    }

    if (type === "fremen-placement-select") {
        return <FremenPlacementSelect args={args} setArgs={setArgs} config={config} />;
    }

    if (type === "integer") {
        return <Integer args={args} setArgs={setArgs} type={config.type} min={config.min} max={config.max} />;
    }

    if (type === "space-select") {
        return <SelectOnMap mode="space-select" args={args} setArgs={setArgs} config={config} interaction={interaction} setInteraction={setInteraction} updateSelection={updateSelection}/>;
    }

    if (type === "space-sector-select-start") {
        return <SelectOnMap mode="space-sector-select-start" args={args} setArgs={setArgs} config={config} interaction={interaction}  setInteraction={setInteraction} updateSelection={updateSelection}/>;
    }

    if (type === "space-sector-select-end") {
        return <SelectOnMap mode="space-sector-select-end" args={args} setArgs={setArgs} config={config} interaction={interaction}  setInteraction={setInteraction} updateSelection={updateSelection}/>;
    }

    if (type === "traitor-select") {
        return <TraitorSelect selected={args} select={setArgs} factionState={state.faction_state[me]}/>;
    }

    if (type === "battle-select") {
        return <SelectOnMap mode="battle-select" setInteraction={setInteraction} setArgs={setArgs} interaction={interaction}  updateSelection={updateSelection}/>;
    }

    if (type === "battle-plan") {
        return <BattlePlan me={me} state={state} args={args} setArgs={setArgs} maxPower={config.max_power} />;
    }

    if (type === "prescience") {
        return <Options options={["leader", "number", "weapon", "defense"]} args={args} setArgs={setArgs} />;
    }

    if (type === "prescience-answer") {
        return <PrescienceAnswer state={state} me={me} args={args} setArgs={setArgs} maxPower={config.max_power} />;
    }

    if (type === "tank-units") {
        return <TankUnits state={state} me={me} args={args} setArgs={setArgs} />;
    }

    if (type === "discard-treachery") {
        return <DiscardTreachery state={state} me={me} args={args} setArgs={setArgs} />;
    }

    if (type === "return-treachery") {
        return <ReturnTreachery state={state} me={me} args={args} setArgs={setArgs} number={config.number} />;
    }

    if (type === "voice") {
        return <Options options={[
            "poison-weapon", "poison-defense", "projectile-weapon", "projectile-defense",
            "no poison-weapon", "no poison-defense", "no projectile-weapon", "no projectile-defense",
            "lasgun", "no lasgun", "worthless", "no worthless", "cheap-hero-heroine", "no cheap-hero-heroine",
        ]} args={args} setArgs={setArgs} />;
    }

    if (type === "revival-units") {
        return <RevivalUnits args={args} setArgs={setArgs} units={config.units} maxUnits={config.maxUnits} single2={config.single2} title={config.title}/>;
    }
    if (type === "revival-leader") {
        return <RevivalLeader args={args} setArgs={setArgs} leaders={config.leaders} required={config.required}/>;
    }
    console.warn(type);

    return <span>
        <span>{(type in humanReadable) ? humanReadable[type] : type}:</span>
        <Input args={args} setArgs={setArgs} config={config} />
    </span>;
};

module.exports = Widget;

