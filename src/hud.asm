; ---------------------------------------------------------------- 4.0: level stats on the world map
; Per level (index from HudIdx): best bananas in one run (word) and "all K-O-N-G collected" (bit).
; Kept in WRAM, packed into the unused tail of the game's save slot (bytes $116-$153).
!HudN      = 36                  ; max levels tracked
!HudIdx    = $403800             ; 256 bytes: main entrance -> level index or $FF
!HudTotal  = $403900             ; level index -> total bananas (word)
!HudTiles  = $7C2100             ; 13 tiles: 0-9, '/', banana, K
!Best      = $7E0454             ; !HudN words
!KongB     = $7E049C             ; 5 bytes of bits
!RunBan    = $7E04A2             ; bananas collected this run
!LastLives = $7E04A4
!HudTmp    = $7E04A6             ; scratch (4 words)
!StatMagic = $5354
!SlotTail  = $0116
!PackN     = 36                  ; packed layout: magic, lo[36], nib[18], kong[5]  = 61 bytes

org $BFD8DE : JSL AddBanana        ; CLC : ADC $057B (every banana added to the counter)
org $BCB99D : JSL LevelDone        ; JSL CODE_809B9C at the start of the level-finished bookkeeping
org $B894EC : JSL LoadPre : NOP #2 ; PHA : JSL CODE_B89470 : PLA (load a file)
org $B89531 : JSL LoadPost : RTS : NOP #5   ; STZ $057F : STZ $057D : STZ $0571 : RTS
org $B89606 : JSL SaveExtra : NOP  ; SEP #$20 : LDX #$0115 (copy save buffer to SRAM slot)
org $80A203 : JSL HudDraw : NOP    ; LDX $8E : CPX #$0400 (hide unused OAM entries at frame end)
!HudFrameNo = $7E04B6
!SlotPtr = $7E04B8

org $405000
AddBanana:
	PHA
	CLC
	ADC.l !RunBan
	STA.l !RunBan
	PLA
	CLC
	ADC.w $057B
	RTL

; returns X = level index * 1 (in A too), or carry set if this level isn't tracked
LevelIndex:                        ; A = main entrance
	AND.w #$00FF
	TAX
	LDA.l !HudIdx,x
	AND.w #$00FF
	CMP.w #$00FF
	BEQ +
	TAX
	CLC
	RTS
+	SEC
	RTS

LevelDone:
	JSL $809B9C
	PHP
	REP #$30
	PHX
	PHY
	PHA
	LDA.l $7E003E
	AND.w #$00FF
	TAX
	LDA.l $BCBABA,x              ; checkpoint / exit entrance -> the level's main entrance
	JSR LevelIndex
	BCS .out
	TXA
	ASL
	TAX
	LDA.l !RunBan
	CMP.l !Best,x
	BCC +
	STA.l !Best,x
+	LDA.l $7E057F                 ; bit 4: the game's "all K-O-N-G found here" flag
	BIT.w #$0010                  ; (the letter bits are swapped for $90 when the 4th is grabbed)
	BNE +
	AND.w #$000F
	CMP.w #$000F
	BNE .out
+
	TXA
	LSR
	JSR BitAddr                  ; X = byte, A = mask
	SEP #$20
	ORA.l !KongB,x
	STA.l !KongB,x
	REP #$20
.out
	PLA
	PLY
	PLX
	PLP
	RTL

BitAddr:                           ; A = index -> X = index/8, A = 1 << (index&7)
	PHA
	LSR
	LSR
	LSR
	TAX
	PLA
	AND.w #$0007
	TAY
	LDA.w #$0001
-	DEY
	BMI +
	ASL
	BRA -
+	RTS

; per map frame: a new run starts here; draw the stats of the level under the Kong
!OamPtr = !HudTmp+8
!PosX   = !HudTmp+2
HudFrame:
	PHP
	REP #$30
	PHX
	PHY
	LDA.w #$0000
	STA.l !RunBan
	LDA.l $7E0575
	STA.l !LastLives
	LDA.l $7E0028
	STA.l !HudFrameNo             ; the map was active this frame
.out0
	PLY
	PLX
	PLP
	RTS

HudDraw:                           ; end of every frame: draw the HUD if the map ran this frame
	PHP
	REP #$30
	PHX
	PHY
	LDA.l $7E0028
	CMP.l !HudFrameNo
	BNE .out
	LDA.l $7E003E
	JSR LevelIndex
	BCS .out
	TXA
	STA.l !HudTmp                ; level index
	LDA.l $7E008E                 ; OAM write pointer
	CMP.w #$0400-(4*10)
	BCS .out
	STA.l !OamPtr
	LDA.l !HudTmp                 ; K icon if all letters were found
	JSR BitAddr
	SEP #$20
	AND.l !KongB,x
	REP #$20
	BEQ +
	LDA.w #8 : STA.l !PosX
	LDA.w #$EC : JSR PutTile
+	LDA.w #20 : STA.l !PosX
	LDA.w #$EB : JSR PutTile      ; banana
	LDA.w #30 : STA.l !PosX
	LDA.l !HudTmp
	ASL
	TAX
	LDA.l !Best,x
	JSR PutNum
	LDA.w #$EA : JSR PutTile      ; '/'
	LDA.l !HudTmp
	ASL
	TAX
	LDA.l !HudTotal,x
	JSR PutNum
	LDA.l !OamPtr
	STA.l $7E008E
.out
	PLY
	PLX
	PLP
	LDX.b $8E
	CPX.w #$0400
	RTL

PutTile:                           ; A = tile; writes one 8x8 OAM entry at !OamPtr, x = !PosX
	PHX
	PHA
	LDA.l !OamPtr
	TAX
	LDA.l !PosX
	SEP #$20
	STA.l $7E0000,x               ; x
	LDA.b #6
	STA.l $7E0001,x               ; y (above the level name)
	PLA
	STA.l $7E0002,x               ; tile
	LDA.b #$34                    ; priority 3, palette 2
	STA.l $7E0003,x
	PLA
	REP #$20
	TXA
	CLC
	ADC.w #4
	STA.l !OamPtr
	LDA.l !PosX
	CLC
	ADC.w #8
	STA.l !PosX
	PLX
	RTS

PutNum:                            ; A = value 0-999, drawn without leading zeros
	STA.l !HudTmp+4
	LDY.w #0                      ; 1 once a digit has been drawn
	LDA.w #100 : JSR .digit
	LDA.w #10 : JSR .digit
	LDY.w #1                      ; always draw the last digit
	LDA.w #1 : JSR .digit
	RTS
.digit
	STA.l !HudTmp+6
	LDX.w #0
	LDA.l !HudTmp+4
-	CMP.l !HudTmp+6
	BCC +
	SEC
	SBC.l !HudTmp+6
	INX
	BRA -
+	STA.l !HudTmp+4
	TXA
	BNE +
	CPY.w #0
	BEQ ++                        ; leading zero: skip
+	LDY.w #1
	CLC
	ADC.w #$E0
	JSR PutTile
++	RTS

; level play: a lost life starts a new run (the bananas come back)
HudLevelFrame:
	PHA
	LDA.l $7E0575
	CMP.l !LastLives
	BEQ +
	BCS ++
	LDA.w #$0000
	STA.l !RunBan
++	LDA.l $7E0575
	STA.l !LastLives
+	PLA
	RTS

; ---- saving: pack into the save slot (pointer [$7A]) after the game's $116 bytes
SaveExtra:
	PHP
	REP #$30
	PHX
	PHY
	LDY.w #!SlotTail
	LDA.w #!StatMagic
	STA.b [$7A],y
	LDX.w #0
-	TXA                           ; low bytes of the best counts
	CLC
	ADC.w #!SlotTail+2
	TAY
	PHX
	TXA
	ASL
	TAX
	LDA.l !Best,x
	PLX
	SEP #$20
	STA.b [$7A],y
	REP #$20
	INX
	CPX.w #!PackN
	BCC -
	LDX.w #0
-	PHX                           ; high nibbles, two levels per byte
	TXA
	ASL
	ASL
	TAX
	LDA.l !Best+1,x
	AND.w #$000F
	STA.l !HudTmp
	LDA.l !Best+3,x
	AND.w #$000F
	ASL
	ASL
	ASL
	ASL
	ORA.l !HudTmp
	STA.l !HudTmp
	PLX
	TXA
	CLC
	ADC.w #!SlotTail+2+!PackN
	TAY
	LDA.l !HudTmp
	SEP #$20
	STA.b [$7A],y
	REP #$20
	INX
	CPX.w #!PackN/2
	BCC -
	LDX.w #0
-	TXA                           ; K-O-N-G bits
	CLC
	ADC.w #!SlotTail+2+!PackN+(!PackN/2)
	TAY
	LDA.l !KongB,x
	SEP #$20
	STA.b [$7A],y
	REP #$20
	INX
	CPX.w #5
	BCC -
	PLY
	PLX
	PLP
	SEP #$20
	LDX.w #$0115
	RTL

; ---- loading
LoadPre:                           ; replaces PHA : JSL CODE_B89470 : PLA  (A = slot index)
	PHA
	JSR ClearStats
	PLA
	PHA
	JSL $B89470
	PHP                           ; keep the carry (file valid)
	REP #$20
	LDA.b $7A                     ; the slot that was actually read
	STA.l !SlotPtr
	PLP
	PLA
	RTL

ClearStats:
	PHP
	REP #$30
	PHX
	LDX.w #0
	LDA.w #0
-	STA.l !Best,x
	INX
	INX
	CPX.w #(!HudN*2)+6
	BCC -
	PLX
	PLP
	RTS

!Base = !HudTmp+2
LoadPost:                          ; replaces STZ $057F : STZ $057D : STZ $0571
	PHP
	REP #$30
	LDA.w #$0000
	STA.l $7E057F
	STA.l $7E057D
	STA.l $7E0571
	PHX
	PHY
	LDA.l !SlotPtr                ; the slot the game just loaded from (bank $B0)
	CLC
	ADC.w #!SlotTail
	STA.l !Base
	TAX
	LDA.l $B00000,x
	CMP.w #!StatMagic
	BEQ +
	JMP .out
+	LDY.w #0
-	TYA                           ; low bytes
	CLC
	ADC.l !Base
	TAX
	LDA.l $B00002,x
	AND.w #$00FF
	PHA
	TYA
	ASL
	TAX
	PLA
	STA.l !Best,x
	INY
	CPY.w #!PackN
	BCC -
	LDY.w #0
-	TYA                           ; high nibbles
	LSR
	CLC
	ADC.l !Base
	TAX
	LDA.l $B00002+!PackN,x
	AND.w #$00FF
	STA.l !HudTmp+6
	TYA
	AND.w #$0001
	BEQ +
	LDA.l !HudTmp+6
	LSR
	LSR
	LSR
	LSR
	STA.l !HudTmp+6
+	LDA.l !HudTmp+6
	AND.w #$000F
	XBA
	STA.l !HudTmp+6
	TYA
	ASL
	TAX
	LDA.l !Best,x
	ORA.l !HudTmp+6
	STA.l !Best,x
	INY
	CPY.w #!PackN
	BCC -
	LDY.w #0
-	TYA                           ; K-O-N-G bits
	CLC
	ADC.l !Base
	TAX
	LDA.l $B00002+!PackN+(!PackN/2),x
	TYX
	SEP #$20
	STA.l !KongB,x
	REP #$20
	INY
	CPY.w #5
	BCC -
.out
	PLY
	PLX
	PLP
	RTL

; ---- 4.1: gold level icons -----------------------------------------------------
; A complete level (best bananas >= total and the K) shows the face of the Kong who beat it
; in gold: DK/Diddy faces (palette 6) move to palette 3, the other faces (palette 2) to 5.
!GoldPal = $403A00                 ; 2 x 15 colours: gold of palette 6, gold of palette 2
GoldIcon:                          ; A = icon attribute, X = entrance, Y = sprite slot. Returns A.
	PHY
	JSL GoldIcon2
	PLY
	RTL
GoldIcon2:
	PHA
	LDA.l $7E0042
	CMP.w #$0002
	BEQ .no                       ; two-player games use palettes 3 and 5 themselves
	TXA
	PHX
	JSR LevelIndex
	BCS .nox
	TXA
	STA.l !HudTmp
	ASL
	TAX
	LDA.l !Best,x
	CMP.l !HudTotal,x
	BCC .nox
	LDA.l !HudTmp
	JSR BitAddr
	SEP #$20
	AND.l !KongB,x
	REP #$20
	BEQ .nox
	PLX
	PLA
	PHA
	AND.w #$0E00
	CMP.w #$0C00
	BNE +
	PLA
	AND.w #$F1FF
	ORA.w #$0600                  ; palette 6 -> 3
	RTL
+	CMP.w #$0400
	BNE .no
	PLA
	AND.w #$F1FF
	ORA.w #$0A00                  ; palette 2 -> 5
	RTL
.nox
	PLX
.no
	PLA
	RTL

GoldPalettes:                      ; after the map's sprite palettes are uploaded (blanking)
	PHP
	REP #$30
	PHX
	LDA.l $7E0042
	CMP.w #$0002
	BEQ .out
	SEP #$20
	LDA.b #$B1                    ; sprite palette 3, colour 1
	STA.l $002121
	REP #$20
	LDX.w #0
-	LDA.l !GoldPal,x
	SEP #$20
	STA.l $002122
	XBA
	STA.l $002122
	REP #$20
	INX
	INX
	CPX.w #30
	BCC -
	SEP #$20
	LDA.b #$D1                    ; sprite palette 5, colour 1
	STA.l $002121
	REP #$20
-	LDA.l !GoldPal,x
	SEP #$20
	STA.l $002122
	XBA
	STA.l $002122
	REP #$20
	INX
	INX
	CPX.w #60
	BCC -
.out
	PLX
	PLP
	RTL
