clear; close all;

results = csvread('results.csv');

lambda = results(1:10, 1);
numHosts1 = results (1, 2);
numHosts2 = results (11, 2);

% Throughputs
throughputs1 = results(1:10, 3);
throughputs2 = results(11:20, 3);

figure;
plot(lambda, throughputs1);
hold on;
plot(lambda, throughputs2, '-.');

title('Throughput vs. Arrival Rate')
xlabel('\lambda');
ylabel('Throughput (b/s)');
legend('10 Hosts', '25 Hosts');
grid on


set(gcf,'PaperUnits','inches','PaperPosition',[0 0 8 6], 'visible', 'off')
print('throughputs.png', '-dpng')



% Average Packet Delays
avgPacketDelays1 = results(1:10, 4);
avgPacketDelays2 = results(11:20, 4);

figure;
plot(lambda, avgPacketDelays1);
hold on;
plot(lambda, avgPacketDelays2, '-.');
axis([-inf inf -inf 0.004])

title('Packet Delay vs. Arrival Rate')
xlabel('\lambda');
ylabel('Packet Delay (s)');
legend('10 Hosts', '25 Hosts')
grid on

set(gcf,'PaperUnits','inches','PaperPosition',[0 0 8 6], 'visible', 'off')
print('packetDelays.png', '-dpng')
