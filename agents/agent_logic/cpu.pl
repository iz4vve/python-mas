dynamic cpu/2, high_priority/1, pingable/1, reachable/1.

underused(Host) :- cpu(Host, Cpu), Cpu<50.
overused(Host) :- cpu(Host, Cpu), Cpu>90.

should_turn_off(Host) :-
    underused(Host),
    \+ requires_ping(Host),
    \+ requires_ssh(Host),
    \+ high_priority(Host).

should_move_or_kill_processes :-
    overused(Host),
    \+ requires_ping(Host),
    \+ requires_ssh(Host),
    \+ high_priority(Host).

requires_ping(Host) :- cpu(Host, Cpu), Cpu=0.
requires_ssh(Host) :- cpu(Host, Cpu), Cpu=0.
