% pingable(Host).
% reachable(Host).
% cpu(Host, Cpu).

underused(Host) :- cpu(Host, Cpu), Cpu<50.
overused(Host) :- cpu(Host, Cpu), Cpu>90.

should_turn_off(Host) :- underused(Host), not(requires_ping(Host)), not(requires_ssh(Host)).
should_move_or_kill_processes :- overused(Host), not(requires_ping(Host)), not(requires_ssh(Host)).

requires_ping(Host) :- cpu(Host, Cpu), Cpu=0.
requires_ssh(Host) :- cpu(Host, Cpu), Cpu=0.
