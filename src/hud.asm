; ---------------------------------------------------------------- 4.x: level stats on the world map
; Every banana (each single in a formation, each banana bunch) has a global number k.
; Collected bananas are remembered per save file and don't come back: the live bitmap sits in
; expanded SRAM at $B0:7000 (the cartridge is now 8 KB SRAM), each file's saved copy at
; $B0:6800 + file*$180. K-O-N-G completion bits stay in the unused tail of the game's save slot.
!HudN      = 36
!HudIdx    = $403800             ; 256 bytes: entrance -> level index or $FF
!HudTotal  = $403900             ; level index -> total bananas (bunch = 10)
!HudTiles  = $7C2100             ; 13 tiles: 0-9, '/', banana, K
!LidTab    = $790000             ; level id -> offset of [N, N x (orig word, k of its lowest bit)]
!BunchTab  = $790200             ; entrance -> offset of [N, N x k-or-$FFFF] (sprite list entries)
!RangeTab  = $790400             ; level index -> offset of [n, n x (k, count, weight)]
!Got       = $B07000             ; live "collected" bitmap (K bits)
!FileArea  = $B06800             ; + file*$180: saved bitmap, magic word at +$17E
!GotBytes  = $0170
!FileMagic = $4247               ; "GB"
!KongB     = $7E049C             ; 5 bytes of bits
!HudTmp    = $7E04A6             ; scratch (5 words)
!HudFrameNo = $7E04B6
!SlotPtr   = $7E04B8
!CurLid    = $7E04BA             ; level id of the formations currently loaded
!CacheEnt  = $7E04BC             ; entrance the HUD numbers were computed for (+1, 0 = none)
!CacheGot  = $7E04BE             ; bananas collected in that level
!StatMagic = $3353             ; "S3" (5.0 layout: K-O-N-G bits, then cabin / save-point bits)
!Stat2Magic = $3253            ; "S2" (4.3 layout: K-O-N-G bits only)
!ShopB     = $7E04A2             ; lo: Cranky's Cabins visited, hi: Candy's Save Points saved at
!OldMagic  = $5354             ; 4.0-4.2 layout: K-O-N-G bits at +56
!SlotTail  = $0116

org $00FFD8 : db $03             ; SRAM size: 8 KB (both headers)
org $40FFD8 : db $03
org $80E9B3 : RTS                ; anti-copier SRAM-size probe (it expects a 2 KB mirror)

org $80833A : JSL FormLoad       ; JSL CODE_B8B580 (level banana formations built)
org $80835D : JSL FormLoad
org $B8BBF9 : JSL Pick           ; EOR [$53],y : STA [$53],y (a banana is picked up)
org $BDFA6F : JSL BunchSpawn : NOP   ; LDX $A4 : LDA $192B,x
org $BFD754 : JSL BunchGot       ; JSL CODE_BCBC37 (a bunch is picked up)
org $B88288 : JSL NewGame        ; JSL CODE_B899DA (fresh game state: progress cleared)
org $BCB99D : JSL LevelDone
org $B894EC : JSL LoadPre : NOP #2
org $B89531 : JSL LoadPost : RTS : NOP #5
org $B89606 : JSL SaveExtra : NOP
org $80A203 : JSL HudDraw : NOP
org $80A35E : JSL Hundred : db $80,$26   ; BRA $80A38A (written raw: asar mis-encodes it here)   ; 100 bananas: extra life but the counter keeps counting

org $405000
; ---- bit helpers on !Got (A = k) ----------------------------------------------------
GotAddr:                           ; A = k -> X = byte offset, A = bit mask (8-bit value)
	PHA
	LSR
	LSR
	LSR
	TAX
	PLA
	AND.w #$0007
	PHX
	TAX
	LDA.l BitMask,x
	AND.w #$00FF
	PLX
	RTS
BitMask: db $01,$02,$04,$08,$10,$20,$40,$80

GotTest:                           ; A = k -> Z clear if collected
	JSR GotAddr
	SEP #$20
	AND.l !Got,x
	REP #$20
	RTS

GotSet:                            ; A = k
	JSR GotAddr
	SEP #$20
	ORA.l !Got,x
	STA.l !Got,x
	REP #$20
	LDA.w #$0000
	STA.l !CacheEnt                ; numbers changed
	RTS

; ---- level start: hide bananas already collected --------------------------------------
FormLoad:
	JSL $B8B580
	PHP
	REP #$30
	PHX
	PHY
	LDA.b $30                     ; level id (formation set)
	AND.w #$00FF
	STA.l !CurLid
	ASL
	TAX
	LDA.l !LidTab,x
	BEQ .out
	TAX                           ; X = offset of [N, ...] in bank $79
	LDA.l $790000,x
	BEQ .out
	STA.l !HudTmp                 ; N words left
	INX
	INX
	LDY.w #$D000                  ; buffer word
.word
	LDA.l $790000,x               ; orig
	STA.l !HudTmp+2
	LDA.l $790002,x               ; k of lowest set bit
	STA.l !HudTmp+4
	LDA.w #$0001
	STA.l !HudTmp+6               ; bit
.bit
	LDA.l !HudTmp+2
	AND.l !HudTmp+6
	BEQ .skip
	PHX
	LDA.l !HudTmp+4
	JSR GotTest
	BEQ .keep
	TYX                           ; collected before: remove it from the level
	LDA.l !HudTmp+6
	EOR.w #$FFFF
	AND.l $7E0000,x
	STA.l $7E0000,x
.keep
	PLX
	LDA.l !HudTmp+4
	INC
	STA.l !HudTmp+4
.skip
	LDA.l !HudTmp+6
	ASL
	STA.l !HudTmp+6
	BNE .bit
	INX
	INX
	INX
	INX
	INY
	INY
	LDA.l !HudTmp
	DEC
	STA.l !HudTmp
	BNE .word
.out
	PLY
	PLX
	PLP
	RTL

; ---- a banana is picked up: A = bits cleared, [$53],y = its word --------------------------
Pick:
	PHA
	EOR.b [$53],y
	STA.b [$53],y
	PHP
	REP #$30
	PHX
	PHY
	TYA
	CLC
	ADC.b $53
	SEC
	SBC.w #$D000
	LSR
	STA.l !HudTmp+8               ; word index j
	LDA.l !CurLid
	ASL
	TAX
	LDA.l !LidTab,x
	BEQ .out
	TAX
	LDA.l !HudTmp+8
	CMP.l $790000,x
	BCS .out
	ASL
	ASL
	CLC
	ADC.w #2
	STA.l !HudTmp+8
	TXA
	CLC
	ADC.l !HudTmp+8
	TAX
	LDA.l $790000,x
	STA.l !HudTmp+2               ; orig
	LDA.l $790002,x
	STA.l !HudTmp+4               ; k
	LDA 6,s                       ; the bits picked up (pushed A)
	STA.l !HudTmp
	LDA.w #$0001
	STA.l !HudTmp+6
-	LDA.l !HudTmp+2
	AND.l !HudTmp+6
	BEQ +
	LDA.l !HudTmp
	AND.l !HudTmp+6
	BEQ ++
	LDA.l !HudTmp+4
	JSR GotSet
++	LDA.l !HudTmp+4
	INC
	STA.l !HudTmp+4
+	LDA.l !HudTmp+6
	ASL
	STA.l !HudTmp+6
	BNE -
.out
	PLY
	PLX
	PLP
	PLA
	RTL

; ---- banana bunches from the level's sprite list -------------------------------------
BunchK:                            ; X = list entry index -> A = k or $FFFF (carry set if none)
	PHX
	LDA.l $7E003E
	AND.w #$00FF
	ASL
	TAX
	LDA.l !BunchTab,x
	BEQ .none
	TAX
	LDA 1,s
	CMP.l $790000,x
	BCS .none
	ASL
	STA.l !HudTmp+8
	TXA
	CLC
	ADC.l !HudTmp+8
	TAX
	LDA.l $790002,x
	CMP.w #$FFFF
	BEQ .none
	PLX
	CLC
	RTS
.none
	PLX
	LDA.w #$FFFF
	SEC
	RTS

BunchSpawn:                        ; replaces LDX $A4 : LDA $192B,x ; A nonzero = don't spawn
	LDX.b $A4
	LDA.w $192B,x
	AND.w #$00FF
	BNE .out
	JSR BunchK
	BCS .zero
	JSR GotTest
	BEQ .zero
	LDX.b $A4
	LDA.w #$0001
	RTL
.zero
	LDX.b $A4
	LDA.w #$0000
.out
	RTL

BunchGot:
	JSL $BCBC37
	PHP
	REP #$30
	PHX
	PHY
	LDX.b $82                     ; this bunch's sprite slot
	LDA.w $15FD,x                 ; its sprite-list entry
	TAX
	JSR BunchK
	BCS +
	JSR GotSet
+	PLY
	PLX
	PLP
	RTL

; ---- K-O-N-G: remembered when the level is finished --------------------------------------
LevelIndex:                        ; A = entrance -> X = level index (carry set if not tracked)
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

KBitAddr:                          ; A = level index -> X = byte, A = mask
	PHA
	LSR
	LSR
	LSR
	TAX
	PLA
	AND.w #$0007
	PHX
	TAX
	LDA.l BitMask,x
	AND.w #$00FF
	PLX
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
	LDA.l $7E057F                 ; bit 4: the game's "all K-O-N-G found here" flag
	BIT.w #$0010
	BNE +
	AND.w #$000F
	CMP.w #$000F
	BNE .out
+	TXA
	JSR KBitAddr
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

; ---- 100 bananas: an extra life, and the counter keeps going -----------------------------
Hundred:                           ; runs when the displayed count is about to go up by one
	LDA.w $0529
	INC
	STA.l !HudTmp
-	CMP.w #100
	BCC .no
	BEQ .life
	SEC
	SBC.w #100
	BRA -
.life
	LDA.w $1E25                   ; the game's own extra-life step
	DEC
	BPL +
	STA.w $1E25
	BRA .no
+	JSL $B6A84B
.no
	RTL

; ---- numbers for a level (cached) ---------------------------------------------------------
; 5.0: "every banana and every K-O-N-G in every level" is checked one level per map frame,
; because the map runs inside NMI and a full pass would overrun the frame.
!DoneIdx = $7E04C8                 ; level being checked
!DoneAcc = $7E04CC                 ; !OkMagic while every level so far is complete
!AllOK   = $7E04A4                 ; result of the last full pass
!OkMagic = $4F4B                   ; "OK" (random power-on RAM can't match by accident)

AllDone:                           ; Z clear (A = 1) if the last full pass found a 100% file
	LDA.l !AllOK
	CMP.w #!OkMagic
	BEQ +
	LDA.w #$0000
	RTS
+	LDA.w #$0001
	RTS

DoneReset:                         ; a file was loaded / started: begin a fresh pass
	LDA.w #$0000
	STA.l !AllOK
	STA.l !DoneIdx
	LDA.w #!OkMagic
	STA.l !DoneAcc
	RTS

!GotFull = 354                     ; bananas are numbered 0-2834: 354 full bytes ...
!GotLast = $07                     ; ... and 3 bits of the next one (build_v2.py asserts this)

DoneStep:                          ; carry set if a pass just finished and the file is NOT 100%
	PHX
	LDA.l !DoneIdx
	CMP.w #!GotFull
	BCS .tail
	TAX
	CLC
	ADC.w #16                     ; 16 bytes of the collected-banana bitmap per frame
	STA.l !DoneIdx
-	LDA.l !Got,x
	CMP.w #$FFFF
	BNE .bad
	INX
	INX
	TXA
	CMP.w #!GotFull
	BCS .clc
	CMP.l !DoneIdx
	BCC -
	BRA .clc
.bad
	LDA.w #$0000
	STA.l !DoneAcc
	LDA.w #!GotFull               ; no need to look further this pass
	STA.l !DoneIdx
	BRA .clc
.tail
	LDA.l !Got+!GotFull
	AND.w #!GotLast
	CMP.w #!GotLast
	BNE .no
	LDA.l !KongB                  ; K-O-N-G in all 33 levels
	CMP.w #$FFFF
	BNE .no
	LDA.l !KongB+2
	CMP.w #$FFFF
	BNE .no
	LDA.l !KongB+4
	AND.w #$0001
	BNE .end
.no
	LDA.w #$0000
	STA.l !DoneAcc
.end
	LDA.l !DoneAcc
	STA.l !AllOK
	LDA.w #!OkMagic
	STA.l !DoneAcc
	LDA.w #$0000
	STA.l !DoneIdx
	LDA.l !AllOK
	CMP.w #!OkMagic
	BEQ .clc
	PLX
	SEC
	RTS
.clc
	PLX
	CLC
	RTS

LevelGot:                          ; X = level index -> A = bananas collected there (bunch = 10)
	TXA
	ASL
	TAX
	LDA.l !RangeTab,x
	TAX
	LDA.l $790000,x
	AND.w #$00FF
	STA.l !HudTmp+2               ; ranges left
	INX
	LDA.w #$0000
	STA.l !HudTmp+4               ; total
-	LDA.l !HudTmp+2
	BEQ .done
	DEC
	STA.l !HudTmp+2
	LDA.l $790000,x               ; k
	STA.l !HudTmp+6
	LDA.l $790002,x               ; count
	STA.l !HudTmp+8
	PHX
--	LDA.l !HudTmp+8
	BEQ +
	DEC
	STA.l !HudTmp+8
	LDA.l !HudTmp+6
	INC
	STA.l !HudTmp+6
	DEC
	JSR GotTest
	BEQ --
	PLX
	PHX
	LDA.l $790004,x               ; weight
	CLC
	ADC.l !HudTmp+4
	STA.l !HudTmp+4
	BRA --
+	PLX
	INX
	INX
	INX
	INX
	INX
	INX
	BRA -
.done
	LDA.l !HudTmp+4
	RTS

; ---- the world map ------------------------------------------------------------------------
!OamPtr = !HudTmp+8
!PosX   = !HudTmp+2
HudFrame:
	PHP
	REP #$30
	LDA.l $7E0028
	STA.l !HudFrameNo             ; the map was active this frame
	PLP
	RTS

HudDraw:                           ; end of every frame: draw the stats if the map ran this frame
	PHP
	REP #$30
	PHX
	PHY
	LDA.l $7E0028
	CMP.l !HudFrameNo
	BEQ +
	JMP .out
+	LDA.l $7E003E
	JSR LevelIndex
	BCC +
	JMP .out
+	TXA
	STA.l !HudTmp                 ; level index
	LDA.l $7E003E
	AND.w #$00FF
	INC
	CMP.l !CacheEnt
	BEQ +
	STA.l !CacheEnt
	LDA.l !HudTmp
	TAX
	JSR LevelGot
	STA.l !CacheGot
	LDA.l $7E003E
	JSR LevelIndex
	TXA
	STA.l !HudTmp
+	LDA.l $7E008E                 ; OAM write pointer
	CMP.w #$0400-(4*10)
	BCC +
	JMP .out
+	STA.l !OamPtr
	LDA.l !HudTmp                 ; K icon if all letters were found
	JSR KBitAddr
	SEP #$20
	AND.l !KongB,x
	REP #$20
	BEQ +
	LDA.w #8 : STA.l !PosX
	LDA.w #$EC : JSR PutTile
+	LDA.w #20 : STA.l !PosX
	LDA.w #$EB : JSR PutTile      ; banana
	LDA.w #30 : STA.l !PosX
	LDA.l !CacheGot
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

PutTile:                           ; A = tile; one 8x8 OAM entry at !OamPtr, x = !PosX
	PHX
	PHA
	LDA.l !OamPtr
	TAX
	LDA.l !PosX
	SEP #$20
	STA.l $7E0000,x
	LDA.b #6
	STA.l $7E0001,x
	PLA
	STA.l $7E0002,x
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

PutNum:                            ; A = value 0-9999, no leading zeros
	STA.l !HudTmp+4
	LDY.w #0
	LDA.w #1000 : JSR .digit
	LDA.w #100 : JSR .digit
	LDA.w #10 : JSR .digit
	LDY.w #1
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
	BEQ ++
+	LDY.w #1
	CLC
	ADC.w #$E0
	JSR PutTile
++	RTS

HudLevelFrame:
	RTS

; ---- saving ----------------------------------------------------------------------------------
FileOff:                           ; -> X = file * $180
	LDA.l $7E0581
	AND.w #$0003
	TAX
	LDA.w #$0000
-	DEX
	BMI +
	CLC
	ADC.w #$0180
	BRA -
+	TAX
	RTS

SaveExtra:                         ; [$7A] = the save slot being written
	PHP
	REP #$30
	PHX
	PHY
	LDA.l $7E003E                  ; 5.0: saved at Candy's ($FA-$FF) -> mark this Save Point
	AND.w #$00FF
	SEC
	SBC.w #$00FA
	CMP.w #$0006
	BCS +
	TAX
	LDA.l BitMask,x
	AND.w #$00FF
	XBA
	ORA.l !ShopB
	STA.l !ShopB
+	LDY.w #!SlotTail+7
	LDA.l !ShopB
	STA.b [$7A],y
	LDY.w #!SlotTail
	LDA.w #!StatMagic
	STA.b [$7A],y
	LDX.w #0
-	TXA
	CLC
	ADC.w #!SlotTail+2
	TAY
	LDA.l !KongB,x
	SEP #$20
	STA.b [$7A],y
	REP #$20
	INX
	CPX.w #5
	BCC -
	JSR FileOff                   ; and the collected-banana bitmap
	TXA
	STA.l !HudTmp
	LDY.w #0
-	TYX
	LDA.l !Got,x
	PHA
	TYA
	CLC
	ADC.l !HudTmp
	TAX
	PLA
	STA.l !FileArea,x
	INY
	INY
	CPY.w #!GotBytes
	BCC -
	JSR FileOff
	LDA.w #!FileMagic
	STA.l !FileArea+$17E,x
	PLY
	PLX
	PLP
	SEP #$20
	LDX.w #$0115
	RTL

LoadPre:
	PHA
	JSR ClearStats
	PLA
	PHA
	JSL $B89470
	PHP
	REP #$20
	LDA.b $7A
	STA.l !SlotPtr
	PLP
	PLA
	RTL

NewGame:
	JSL $B899DA
	JSR ClearStats
	JSR ValidateFlags
	RTL

ClearStats:
	PHP
	REP #$30
	PHX
	LDA.w #0
	LDX.w #0
-	STA.l !KongB,x
	INX
	INX
	CPX.w #8                      ; K-O-N-G bits and the cabin / save-point bits
	BCC -
	LDX.w #0
-	STA.l !Got,x
	INX
	INX
	CPX.w #!GotBytes
	BCC -
	STA.l !CacheEnt
	JSR DoneReset
	PLX
	PLP
	RTS

LoadPost:
	PHP
	REP #$30
	LDA.w #$0000
	STA.l $7E057F
	STA.l $7E057D
	STA.l $7E0571
	STA.l !CacheEnt
	PHX
	PHY
	LDA.l !SlotPtr
	CLC
	ADC.w #!SlotTail
	TAX
	LDA.l $B00000,x
	CMP.w #!OldMagic
	BNE ++
	TXA
	CLC
	ADC.w #54
	TAX
	BRA +++
++	CMP.w #!StatMagic
	BNE ++++
	LDA.l $B00007,x                ; 5.0: cabin / save-point bits
	STA.l !ShopB
	LDA.l $B00000,x
++++	CMP.w #!Stat2Magic
	BEQ +++
	CMP.w #!StatMagic
	BNE +
+++	LDY.w #0
-	LDA.l $B00002,x
	PHX
	TYX
	SEP #$20
	STA.l !KongB,x
	REP #$20
	PLX
	INX
	INY
	CPY.w #5
	BCC -
+	JSR FileOff
	LDA.l !FileArea+$17E,x
	CMP.w #!FileMagic
	BNE .out
	TXA
	STA.l !HudTmp
	LDY.w #0
-	TYA
	CLC
	ADC.l !HudTmp
	TAX
	LDA.l !FileArea,x
	TYX
	STA.l !Got,x
	INY
	INY
	CPY.w #!GotBytes
	BCC -
.out
	JSR ValidateFlags
	PLY
	PLX
	PLP
	RTL

; ---- gold level icons ------------------------------------------------------------------------
!GoldPal = $403A00
GoldIcon:                          ; A = icon attribute, X = entrance, Y = sprite slot
	PHY
	JSL GoldIcon2
	PLY
	RTL
GoldIcon2:
	PHA
	LDA.l $7E0042
	CMP.w #$0002
	BEQ .no
	TXA
	PHX
	JSR LevelIndex
	BCS .nox
	TXA
	STA.l !HudTmp
	JSR KBitAddr
	SEP #$20
	AND.l !KongB,x
	REP #$20
	BEQ .nox
	LDA.l !HudTmp
	TAX
	JSR LevelGot
	PHA
	LDA.l !HudTmp
	ASL
	TAX
	PLA
	CMP.l !HudTotal,x
	BCC .nox
	PLX
	PLA
	PHA
	AND.w #$0E00
	CMP.w #$0C00
	BNE +
	PLA
	AND.w #$F1FF
	ORA.w #$0600
	RTL
+	CMP.w #$0400
	BNE .no
	PLA
	AND.w #$F1FF
	ORA.w #$0A00
	RTL
.nox
	PLX
.no
	PLA
	RTL

GoldPalettes:
	PHP
	REP #$30
	PHX
	LDA.l $7E0042
	CMP.w #$0002
	BEQ .out
	SEP #$20
	LDA.b #$B1
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
	LDA.b #$D1
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
