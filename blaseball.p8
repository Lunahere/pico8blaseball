pico-8 cartridge // http://www.pico-8.com
version 32
__lua__
--blaseball viewer
--by lunahere

function _init()
	ticker_text=""
	date_text=""
	state=0
	writeto=0x0
	g_log=""
	pos="home"
	score={home={"0","0"},away={"0","0"}}
	in_pos=1
	half_inning={0,0,0}
	sb_pos=1
	scoreboard={0,0,0}
	b_pos=1
	bases={{{},{}},{0,0}}
	turn={"",""}
	t_pos="home"
	teams={home="",away=""}
	home_name,away_name="",""
	inning={{"0","0"},true}
	w_text=""
	w_out=""
	player_names={home={"",""},away={"",""}}
	pn_pos="home"
end

function _update60()
	state=max(state,0)
	stdout=serial(0x804,writeto,1)

	if stdout>0 then
		read=chr(peek(writeto))
		if read=="<" then
			state-=1
		elseif read==">" then
			state+=1
		elseif read=="|" then
			state=0
		elseif state==0 then	--ticker
			ticker_text=ticker_text..read
			ticker_text=sub(ticker_text,-32)
		elseif state==2 then	--game log
			if read=="_" then
				g_log=""
			else
				sfx(0)
				g_log=g_log..read
				if (#g_log+1)%16==0 then
					g_log=g_log.."\n"
				end
			end
		elseif state==3 then	--score
			if read=="_" then
				pos="home"
				score.home[1]=""
			elseif read=="^" then
				pos="away"
				score.away[1]=""
			elseif read=="=" then
				for _,t in pairs(score) do
					if t[1]=="" then
						t[1]="0"
					end
					t[2]=t[1]
				end
			else
				score[pos][1]=score[pos][1]..read
			end
		elseif state==4 then	--scoreboard points
			if read=="_" then
				in_pos=1
			elseif read=="^" then
				in_pos=2
			elseif read=="." then
				in_pos=3
			else
				half_inning[in_pos]=tonum(read)
			end
		elseif state==5 then	--scoreboard
			if read=="_" then
				sb_pos=1
			elseif read=="^" then
				sb_pos=2
			elseif read=="." then
				sb_pos=3
			else
				scoreboard[sb_pos]=tonum(read)
			end
		elseif state==6 then	--bases
			if read=="_" then
				bases[1][1]={}
				bases[2][1]=0
				b_pos=1
			elseif read=="^" then
				b_pos=2
			elseif read=="=" then
				bases[2][2]=bases[2][1]
				bases[1][2]=bases[1][1]
			elseif b_pos==1 then
				add(bases[1][1],tonum(read))
			elseif b_pos==2 then
				bases[2][1]=tonum(read)
			end
		elseif state==7 then	--play count
			if read=="_" then
				turn[1]=""
			elseif read=="=" then
				turn[2]=turn[1]
			else
				turn[1]=turn[1]..read
			end
		elseif state==8 then --team names
			if read=="_" then
				teams[t_pos]=""
			elseif read=="^" then
				t_pos="home"
			elseif read=="." then
				t_pos="away"
			elseif read=="=" then
				home_name=teams.home
				away_name=teams.away
			else
				teams[t_pos]=teams[t_pos]..read
			end
		elseif state==9 then --inning
			if read=="_" then
				inning[1][1]=""
			elseif read=="^" then
				inning[2]=true
			elseif read=="." then
				inning[2]=false
			elseif read=="=" then
				if inning[1][1]~=inning[1][2] then
					inning[1][2]=inning[1][1]
				end
			else
				inning[1][1]=inning[1][1]..read
			end
		elseif state==10 then --weather
			if read=="_" then
				w_text=""
			elseif read=="=" then
				w_out=w_text
			else
				w_text=w_text..read
			end
		elseif state==11 then --player names
			if read=="_" then
				pn_pos="home"
				player_names.home[1]=""
			elseif read=="^" then
				pn_pos="away"
				player_names.away[1]=""
			elseif read=="=" then
				player_names.home[2] = player_names.home[1]
				player_names.away[2] = player_names.away[1] 
			else
				player_names[pn_pos][1]=player_names[pn_pos][1]..read
			end
		elseif state==1 then --date
			if read=="_" then
				date_text=""
				date_done=false
			elseif read=="." then
				date_done=true
			elseif date_done~=true then
				date_text=date_text..read
			end
		end
	end
end

function _draw()
	cls()
	print(ticker_text,0,0,6)
	pset(state,6,6)
	print(date_text,64-#date_text/2*4,7)
	print(w_out,64-#w_out/2*4,14)
	rect(64,64,127,127,6)
	draw_score()
	draw_scoreboard()
	draw_half_inning()
	draw_bases()
	print(turn[2],64-#turn[2]*4,123,6)
	print(g_log,66,66,6)
	sspr(0,0,8,1,state+1,6)
end

function draw_score()
	local x,y=111,15
	print(score.away[2],x,y*2)
	print("("..player_names.away[2]..")",x-14-#away_name*4-#player_names.away[2]*4,y*2)
	print(away_name,x-5-#away_name*4,y*2)
	print(score.home[2],x,y*3)
	print("("..player_names.home[2]..")",x-14-#home_name*4-#player_names.home[2]*4,y*3)
	print(home_name,x-5-#home_name*4,y*3)

	print(inning[1][2],x+12-#inning[1][2]*4,y*2+7)
	
	if inning[2] then
		line(x+13,y*2+8,x+15,y*2+8,6)
		pset(x+14,y*2+7,6)
	else
		line(x+13,y*2+9,x+15,y*2+9,6)
		pset(x+14,y*2+10,6)
	end
end

function draw_half_inning()
	local x,y=32,64
	print("balls",x-21,y,6)
	print("strikes",x-29,y+6,6)
	print("outs",x-17,y+12,6)
	for k,s in pairs(half_inning) do
		for i=0,s-1 do
			circfill(x+i*6+3,y+(k-1)*6+2,2,6)
		end
	end
end

function draw_scoreboard()
	local x,y=32,64
	for k,s in pairs(scoreboard) do
		for i=0,s-1 do
			circ(x+i*6+3,y+(k-1)*6+2,2,6)
		end
	end
end

function draw_base(x,y)
	line(x+1,y+8,x+15,y+8,6)
	line(x+8,y+1,x+8,y+15)
	rectfill(x+2,y+7,x+14,y+9)
	rectfill(x+3,y+6,x+13,y+10)
	rectfill(x+4,y+5,x+12,y+11)
	rectfill(x+5,y+4,x+11,y+12)
	rectfill(x+6,y+3,x+10,y+13)
	rectfill(x+7,y+2,x+9,y+14)
end

function draw_base_empty(x,y)
	line(x+8,y,x+16,y+8,6)
	line(x+16,y+8,x+8,y+16)
	line(x+8,y+16,x,y+8)
	line(x,y+8,x+8,y)
end

function draw_bases()
	local x,y=31,90
	for i=1,bases[2][2] do
		draw_base_empty(x-(i)*9+2+((bases[2][2]-3)*9*(0.5^(bases[2][2]-3))+8),y+(i%2)*9)
	end
	for i in all(bases[1][2]) do
		draw_base(x-(i)*9+2+((bases[2][2]-3)*9*(0.5^(bases[2][2]-3))+8),y+(i%2)*9)
	end
end

__gfx__
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00700700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00077000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00077000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00700700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
__sfx__
4d0100000c5231852315523205231c5031d5031e5031f503205032050320503205032050320503205031f5031f5031e5031d5031c5031b5031a5031950317503165031350311503105030f503105031250314503
491000031052014520215000f500105001150012500135001450015500165001750018500195001a5001b5001c5001d5001e5001f500205002150022500235002450025500265002750028500295002a5002c500
991000031b120151202a100291002810027100261002510024100231002210021100201001f1001e1001d1001c1001b1001a100191001810017100161001510014100131001210011100101000f1000e1000d100
010700001e6001e600000001c6001c6001d600000001d6001d6001d60000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
