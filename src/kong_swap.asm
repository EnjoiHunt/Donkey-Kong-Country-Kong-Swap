; DKC1 Kong Swap 3.0 — on the overworld, R cycles DK -> Kiddy -> Cranky and L cycles Diddy -> Dixie -> Candy.
; Applied with asar on top of the 8 MB ExHiROM image prepared by build_v2.py.
exhirom

!KFlag     = $7E04C0        ; !Magic = Kiddy replaces DK, !Magic2 = Cranky
!DFlag     = $7E04C2        ; !Magic = Dixie replaces Diddy, !Magic2 = Candy
!GhostKind = $7E04C4        ; ghost palette last written to sprite palette 0 (1 DK/Diddy, 2 Kiddy/Dixie)
!PalWant   = $7E04C6        ; scratch: palette bits wanted for a map Kong sprite
!GhostPal  = $403500        ; 3 x 15 colours (DK/Diddy, Kiddy/Dixie, Cranky/Candy)
!Magic2    = $4343          ; "CC"
!TabC      = $7A0000        ; frame table with Cranky entries
!TabY      = $7A3000        ; frame table with Candy entries
!AltPalettes2 = $403600     ; copy of $BC:8422-$BC:8511 with Cranky/Candy palettes
!MapPalCC  = $403700        ; 15 colours: Cranky & Candy on the map (sprite palette 4)
!MapPal4   = $F9BF85        ; original colours of map sprite palette 4
!CCFaces   = $7C2000        ; Cranky/Candy face tiles ($6C-$6F, $7C-$7F)
!Magic     = $4B44          ; "KD" - random power-on RAM can't match by accident
!PalTemp   = $7E04F2
!BlkSrc    = $7E04F6
!BlkCnt    = $7E04F8
!BlkCG     = $7E04FA
!BlkTmp    = $7E04FC
!GlideOn   = $7E04E0        ; frame number of Dixie's latest glide frame
!GlideSlot = $7E04E2        ; her sprite slot
!GlideLo   = $7E04E4        ; frame pointer to draw instead of her pose
!GlideHi   = $7E04E6
!GlideCnt  = $7E04E8
!GlideTbl  = $403200        ; 12 x 4-byte pointers to the spin frames
!GlideFall = $FEC0
!PoundStamp = $7E04D0       ; frame number of Kiddy's latest slam frame (pose override)
!PoundSlot  = $7E04D2
!PoundLo    = $7E04D4
!PoundHi    = $7E04D6
!PoundCnt   = $7E04D8
!PoundOn    = $7E04DA       ; 1 while a ground pound is in progress
!PoundLast  = $7E04DC       ; last frame the Kiddy routine ran
!PoundTbl   = $403300       ; 4-byte pointers to Kiddy's slam (somersault) frames
!PoundY     = $7E04DE       ; height where the pound started (held during the flip)
!PoundSit   = $7E04CE       ; 1 while Kiddy stays seated after a pound
!PoundHang  = 20           ; frames of mid-air pause while flipping
!PoundSlam  = 10           ; table entry of the butt-slam pose
!PoundFall  = $F700         ; slam speed (faster than normal max fall $F800)          ; slowest fall speed while gliding (normal max is $F800)        ; 1 while redirecting the palette being queued
!MapPalOn  = $7E04F4        ; last palette state queued for the map sprite

!PoseTable    = $BBCC9C      ; original DKC1 sprite pose (frame pointer) table
!AltPoseTable = $400000      ; frame table with Kiddy AND Dixie entries
!TabK         = $7D0000      ; frame table with Kiddy entries only
!TabD         = $7D3000      ; frame table with Dixie entries only
!AltPalettes  = $403000      ; copy of $BC:8422-$BC:8511 with Kiddy/Dixie palettes
!KongPalLo    = $8422
!KongPalHi    = $8512
!MapPalKiddy  = $403100      ; 15 colours for the overworld Kiddy sprite
!MapPalDK     = $F9BF25      ; original colours of map sprite slot 1 (player-2 Kong)

!PressedButtons = $7E0510
!MapTimerA      = $7E1DF5
!MapTimerB      = $7E1DF7
!DisplayedPose  = $7E0AE5    ; per-sprite, indexed by sprite slot
!CurIndex       = $82        ; direct page: current sprite slot
!PalQueueIdx    = $7E1AD1
!PalQueuePtr    = $7E1A8F
!PalQueueBank   = $7E1A91
!ScreenShadow   = $7E051A    ; game copy of INIDISP

; ---------------------------------------------------------------- hooks ---

incsrc "hud.asm"

org $BBA724 : JSL PoseLo     ; four places read the pose table (low word / bank)
org $BBA72A : JSL PoseHi
org $BBA7AB : JSL PoseLo
org $BBA7B4 : JSL PoseHi
org $BBA890 : JSL PoseLo
org $BBA899 : JSL PoseHi
org $81938B : JSL PoseLo
org $81937F : JSL PoseHi

org $BDF274                  ; LDA $8C : STA PtrLo,x   (sprite palette upload queue)
	JSL PalLo
	NOP
org $BDF283                  ; ORA #$00BC : STA PtrBank,x
	JSL PalBank
	NOP #2

org $80D199                  ; overworld DK sprite: button handling
	JSL MapHook
	db $80,$08                ; BRA $80D1A7 (written raw: asar mis-encodes cross-mapper BRA)
	NOP #8



; anti-copier SRAM probe: use $B0 (valid SRAM in HiROM *and* ExHiROM) instead of $30
org $80E9B6 : db $B0
org $80E9BB : db $B0
org $80E9BF : db $B0
org $80E9C6 : db $B0
org $80E9CA : db $B0
org $80E9CF : db $B0
org $80E9D3 : db $B0
org $80E9DA : db $B0


; dark / rain / lightning levels build a filtered RAM copy of $BC:81CC - feed it Kiddy/Dixie colours
org $8198DE : JSL PalBuf0
org $8198EE : JSL PalBuf0
org $819902 : JSL PalBuf0
org $819932 : JSL PalBuf0
org $819949 : JSL PalBuf0
org $81996F : JSL PalBuf0
org $819979 : JSL PalBuf0
org $81998A : JSL PalBuf0
org $8199A9 : JSL PalBuf0
org $819A0A : JSL PalBuf0
org $819A15 : JSL PalBuf0
org $819A31 : JSL PalBuf0
org $819A3B : JSL PalBuf0
org $819A4F : JSL PalBuf0
org $819A75 : JSL PalBuf0
org $819A80 : JSL PalBuf0
org $819A9C : JSL PalBuf0
org $819AB0 : JSL PalBuf0
org $819AC8 : JSL PalBuf0
org $B6B38B : JSL PalBuf0
org $B6B3AD : JSL PalBuf0
org $B6B3CF : JSL PalBuf0
org $B6B3FD : JSL PalBuf2
org $B6B41F : JSL PalBuf2
org $B6B441 : JSL PalBuf2

; generic palette-block upload (CODE_B999F1): remember the request, then patch Kong slots
org $B999F1 : JSL PalPre
org $B99A0E
	JML PalPost
	NOP #2

; Dixie's helicopter spin: runs at the start of the Diddy-slot sprite's main routine each frame
org $BF849F
	JSL DixieGlide              ; replaces LDA #$0002 : STA $84
	NOP

; Held barrels (CODE_BFCCDB): when Kiddy holds one, sit it in front of his chest
org $BFCCEA : JSL BarrelXR : NOP #2     ; ADC $13E9,x : STA $0B19,x
org $BFCCF6 : JSL BarrelXL : NOP #2     ; SBC $13E9,x : STA $0B19,x
org $BFCD00 : JSL BarrelY  : NOP #2     ; ADC $145D,x : STA $0BC1,x

; Kiddy's ground pound: shared Kong entry (DK and Diddy both pass through here)
org $BF84A8
	JSL KongMain                ; replaces LDX $84 : LDA $16FD,x
	NOP

; attack box for the pound, in free space of bank $BB (used by CODE_BBA4E5)
org $BBB160
PoundBox:
	dw $FFF0,$FFFA,$0020,$0018  ; x -16, top 6 px above the feet, 32 wide, 24 tall

; Level-complete faces: Kiddy / Dixie get their own map icons
org $80E2EA : NOP #2          ; world map: always spawn the second Kong (a ghost if absent)
org $80E6E8                     ; icon animation DMA source (8 frames, now 0x400 bytes each)
	JSL IconSrc
	NOP #5
org $80E6F1 : JSL IconDMA       ; after the icon DMA, also upload the Cranky/Candy faces
org $80E5AA                     ; icon attribute store: pick Kiddy/Dixie face for values 5/6
	JSL IconAttr
	NOP #2
org $BCB9B9                     ; level finished: remember who did it (5 = Kiddy, 6 = Dixie)
	JSL WhoBeat

; ----------------------------------------------------------------- code ---
org $404000

PoseLo:
	LDA.l $7E0028
	SEC
	SBC.l !PoundStamp
	CMP.w #2
	BCS +
	TYA
	CMP.l !PoundSlot
	BNE +
	LDA.l !PoundLo
	RTL
+	LDA.l $7E0028               ; frame counter
	SEC
	SBC.l !GlideOn              ; = frame number Dixie last glided
	CMP.w #2
	BCS +
	TYA
	CMP.l !GlideSlot
	BNE +
	LDA.l !GlideLo
	RTL
+	TXA
	JSR PoseSide                ; which Kong's table: by the side this pose belongs to
	BNE .small
	LDA.l !KFlag
	CMP.w #!Magic : BEQ .k
	CMP.w #!Magic2 : BEQ .c
.o	LDA.l !PoseTable,x
	RTL
.small
	LDA.l !DFlag
	CMP.w #!Magic : BEQ .d
	CMP.w #!Magic2 : BEQ .y
	BRA .o
.k	LDA.l !TabK,x
	RTL
.c	LDA.l !TabC,x
	RTL
.d	LDA.l !TabD,x
	RTL
.y	LDA.l !TabY,x
	RTL

PoseHi:
	LDA.l $7E0028
	SEC
	SBC.l !PoundStamp
	CMP.w #2
	BCS +
	TYA
	CMP.l !PoundSlot
	BNE +
	LDA.l !PoundHi
	RTL
+	LDA.l $7E0028               ; frame counter
	SEC
	SBC.l !GlideOn              ; = frame number Dixie last glided
	CMP.w #2
	BCS +
	TYA
	CMP.l !GlideSlot
	BNE +
	LDA.l !GlideHi
	RTL
+	TXA
	JSR PoseSide                ; which Kong's table: by the side this pose belongs to
	BNE .small
	LDA.l !KFlag
	CMP.w #!Magic : BEQ .k
	CMP.w #!Magic2 : BEQ .c
.o	LDA.l !PoseTable+2,x
	RTL
.small
	LDA.l !DFlag
	CMP.w #!Magic : BEQ .d
	CMP.w #!Magic2 : BEQ .y
	BRA .o
.k	LDA.l !TabK+2,x
	RTL
.c	LDA.l !TabC+2,x
	RTL
.d	LDA.l !TabD+2,x
	RTL
.y	LDA.l !TabY+2,x
	RTL

PalLo:
	LDA.w #$0000
	STA.l !PalTemp
	LDA.b $8C
	CMP.w #!KongPalLo
	BCC .orig
	CMP.w #!KongPalHi
	BCS .orig
	CMP.w #$849A                ; $8422-$8499 Diddy palettes, $849A-$8511 DK palettes
	BCC .dix
	LDA.l !KFlag
	BRA .chk
.dix
	LDA.l !DFlag
.chk
	CMP.w #!Magic2
	BEQ .cc
	CMP.w #!Magic
	BNE .orig
	LDA.b $8C
	CLC
	ADC.w #(!AltPalettes&$FFFF)-!KongPalLo
	BRA .alt
.cc
	LDA.b $8C
	CLC
	ADC.w #(!AltPalettes2&$FFFF)-!KongPalLo
.alt
	STA.w $1A8F,x
	LDA.w #$0001
	STA.l !PalTemp
	RTL
.orig
	LDA.b $8C
	STA.w $1A8F,x
	RTL

PalBank:
	ORA.w #$00BC
	PHA
	LDA.l !PalTemp
	BEQ .orig
	PLA
	AND.w #$FF00
	ORA.w #!AltPalettes>>16
	STA.w $1A91,x
	RTL
.orig
	PLA
	STA.w $1A91,x
	RTL

; Runs every frame for the overworld DK sprite (replaces 14 bytes at $80D199).
MapHook:
	JSR KongPalSlot
	JSR HudFrame
	LDA.l !PressedButtons
	BEQ .noPress
	STA.l !MapTimerA
	LDA.w #$0020
	STA.l !MapTimerB
	LDA.l !PressedButtons
	AND.w #$0030              ; L or R
	BEQ .noPress
	BIT.w #$0010              ; R: primary Kong (DK -> Kiddy -> Cranky)
	BEQ +
	LDA.l !KFlag
	JSR NextKong
	STA.l !KFlag
+	LDA.l !PressedButtons
	BIT.w #$0020              ; L: secondary Kong (Diddy -> Dixie -> Candy)
	BEQ +
	LDA.l !DFlag
	JSR NextKong
	STA.l !DFlag
+
	LDX.w #$0032              ; force every sprite (both map Kongs) to re-upload its frame
	LDA.w #$0000
-	STA.l !DisplayedPose,x
	DEX
	DEX
	BPL -
	LDA.w #$0001              ; rewrite the palette below
	STA.l !MapPalOn
.noPress
	; on a switch, rewrite sprite palette 6 (colours 225-239) right away
	LDA.l !MapPalOn
	BEQ .done
	LDA.w #$0000
	STA.l !MapPalOn
	PHX
	PHP
	SEP #$20
	LDA.b #$80                ; brief forced blank so CGRAM accepts the write
	STA.l $002100
	LDA.b #$91                ; sprite palette slot 1, colour 1
	STA.l $002121
	REP #$20
	LDX.w #$0000
	JSR AnyFlag
	BEQ .dkLoop
.kidLoop
	LDA.l !MapPalKiddy,x
	SEP #$20
	STA.l $002122
	XBA
	STA.l $002122
	REP #$20
	INX
	INX
	CPX.w #30
	BCC .kidLoop
	BRA .restore
.dkLoop
	LDA.l !MapPalDK,x
	SEP #$20
	STA.l $002122
	XBA
	STA.l $002122
	REP #$20
	INX
	INX
	CPX.w #30
	BCC .dkLoop
.restore
	JSR CCMapPalette
	JSR GhostPalette
	SEP #$20
	LDA.l !ScreenShadow
	STA.l $002100
	PLP
	PLX
.done
	RTL


; ---- RAM palette buffer sources ($BC:81CC + X); Kong palettes live at X = $0256-$0345
PalBuf0:
	CPX.w #$0256
	BCC .orig
	CPX.w #$0346
	BCS .orig
	CPX.w #$02CE                ; below: Diddy palettes, above: DK palettes
	BCC +
	LDA.l !KFlag
	BRA ++
+	LDA.l !DFlag
++	CMP.w #!Magic2
	BEQ .cc
	CMP.w #!Magic
	BNE .orig
	LDA.l (!AltPalettes&$FFFFFF)-$0256,x
	RTL
.cc
	LDA.l (!AltPalettes2&$FFFFFF)-$0256,x
	RTL
.orig
	LDA.l $BC81CC,x
	RTL

PalBuf2:
	CPX.w #$0254
	BCC .orig
	CPX.w #$0344
	BCS .orig
	CPX.w #$02CC
	BCC +
	LDA.l !KFlag
	BRA ++
+	LDA.l !DFlag
++	CMP.w #!Magic2
	BEQ .cc
	CMP.w #!Magic
	BNE .orig
	LDA.l (!AltPalettes&$FFFFFF)-$0254,x
	RTL
.cc
	LDA.l (!AltPalettes2&$FFFFFF)-$0254,x
	RTL
.orig
	LDA.l $BC81CE,x
	RTL

; ---- palette blocks from bank $B9 (shops, map, menus)
PalPre:
	STA.w $4302
	STA.l !BlkSrc
	TXA
	STA.l !BlkCnt
	TYA
	STA.l !BlkCG
	TXA
	RTL

PalPost:                      ; entered by JML with 8-bit A = #$01
	STA.w $420B
	REP #$20
	LDA.l !BlkSrc
	CMP.w #$BF03                ; map / island sprite palettes: add the face colours
	BNE +
	JSR FacePalette
	JSR GhostPalette
	JSR CCMapPalette
+
	PHX
	PHY
	LDA.l !BlkCnt
	ASL
	ASL
	ASL
	STA.l !BlkTmp                ; block size in bytes
	LDY.w #$0000
.next
	TYX
	LDA.l BlockTable,x
	BEQ .done
	LDA.l BlockTable+4,x        ; which Kong this entry belongs to
	JSR FlagFor
	BEQ .skip
	LDA.l BlockTable,x
	SEC
	SBC.l !BlkSrc
	CMP.l !BlkTmp
	BCS .skip
	LSR                           ; byte offset -> colour index
	CLC
	ADC.l !BlkCG
	SEP #$20
	STA.l $002121
	REP #$20
	LDA.l BlockTable+2,x
	TAX
	PHY
	LDY.w #15
.col
	LDA.l $400000,x
	SEP #$20
	STA.l $002122
	XBA
	STA.l $002122
	REP #$20
	INX
	INX
	DEY
	BNE .col
	PLY
.skip
	INY
	INY
	INY
	INY
	INY
	INY
	BRA .next
.done
	PLY
	PLX
.out
	RTL

; (address of colour 1 inside a $B9 palette block, replacement colours in bank $40)
!KidPal = (!AltPalettes&$FFFF)+($849A-$8422)
!DixPal = (!AltPalettes&$FFFF)
!CraPal = (!AltPalettes2&$FFFF)+($849A-$8422)
!CanPal = (!AltPalettes2&$FFFF)
BlockTable:
	dw $B785,!KidPal,0          ; title / intro screen
	dw $B905,!KidPal,0          ; Funky's Flights
	dw $B925,!DixPal,1
	dw $BA85,!KidPal,0          ; menu block 6
	dw $BAA5,!DixPal,1
	dw $BBC5,!KidPal,0          ; menu block 7 (player 2 colours)
	dw $BBE5,!DixPal,1
	dw $BC65,!KidPal,0          ; Candy's Save Point
	dw $BC85,!DixPal,1
	dw $BDA5,!KidPal,0          ; Cranky's Cabin
	dw $BDC5,!DixPal,1
	dw $E247,!KidPal,0          ; block 9
	dw $E267,!DixPal,1
	dw $BF25,!MapPalKiddy&$FFFF,2  ; world map: Kiddy & Dixie get sprite palette slot 1
	dw $B785,!CraPal,3
	dw $B905,!CraPal,3
	dw $B925,!CanPal,4
	dw $BA85,!CraPal,3
	dw $BAA5,!CanPal,4
	dw $BBC5,!CraPal,3
	dw $BBE5,!CanPal,4
	dw $BC65,!CraPal,3
	dw $BC85,!CanPal,4
	dw $BDA5,!CraPal,3
	dw $BDC5,!CanPal,4
	dw $E247,!CraPal,3
	dw $E267,!CanPal,4
	dw $0000

; Map Kong sprites (IDs $10 MapDK, $12 MapDiddy, $14 JumpingKong, $1C LeavingKong) use
; palette slot 6, shared with path dots and level markers. With Kiddy & Dixie selected,
; move them to slot 1 (only used by player 2 in two-player games) and back again after.
!SprID   = $7E0D45
!SprAttr = $7E0C69
!SlotMark = $7E0420
KongPalSlot:
	JSR GhostSel                ; lead or flags changed -> rewrite the map palettes
	CMP.l !GhostKind
	BEQ +
	LDA.w #$0001
	STA.l !MapPalOn
+	PHX
	LDX.w #$0032
.loop
	LDA.l !SprID,x
	CMP.w #$0010 : BEQ .kong
	CMP.w #$0012 : BEQ .kong
	CMP.w #$0014 : BEQ .kong
	CMP.w #$001C : BEQ .kong
	BRA .next
.kong
	LDA.l $7E0D11,x             ; current pose -> which Kong this map sprite is
	JSR PoseSide                ; A = 0 big Kong, 1 small Kong
	PHA
	LDA.l $7E0579               ; partner missing and this isn't the lead Kong -> ghost
	AND.w #$0001
	BNE .real
	LDA.l $7E056F
	DEC
	CMP 1,s
	BEQ .real
	PLA
	LDA.w #$0000                ; sprite palette 0 = ghost colours
	BRA .apply
.real
	PLA
	JSR KongOf                  ; A = flag value of that side
	CMP.w #!Magic2
	BNE +
	LDA.w #$0800                ; palette 4 = Cranky / Candy map colours
	BRA .apply
+	CMP.w #!Magic
	BNE .six
	LDA.w #$0200                ; palette 1 = Kiddy / Dixie map colours
	BRA .apply
.six
	LDA.w #$0C00                ; palette 6 = original DK / Diddy
.apply
	STA.l !PalWant
	LDA.l !SprAttr,x
	AND.w #$0E00
	CMP.w #$0C00 : BEQ .set
	CMP.w #$0200 : BEQ .set
	CMP.w #$0800 : BEQ .set
	CMP.w #$0000 : BNE .next
.set
	LDA.l !SprAttr,x
	AND.w #$F1FF
	ORA.l !PalWant
	STA.l !SprAttr,x
.next
	DEX
	DEX
	BMI +
	JMP .loop
+	PLX
	RTS

GhostSel:                       ; A = 1 DK/Diddy, 2 Kiddy/Dixie, 3 Cranky/Candy (the non-lead Kong)
	LDA.l $7E056F
	CMP.w #$0001
	BEQ +
	LDA.w #$0000                ; Diddy-side leads: ghost is the big Kong
	BRA ++
+	LDA.w #$0001
++	JSR KongOf
	CMP.w #!Magic
	BNE +
	LDA.w #$0002
	RTS
+	CMP.w #!Magic2
	BNE +
	LDA.w #$0003
	RTS
+	LDA.w #$0001
	RTS

GhostPalette:                   ; sprite palette 0, colours 1-15 (call during blanking)
	PHX
	PHY
	PHP
	REP #$30
	JSR GhostSel
	STA.l !GhostKind
	DEC
	STA.l !PalWant
	ASL
	ASL
	ASL
	ASL
	SEC
	SBC.l !PalWant
	ASL                         ; (kind-1) * 30
	TAX
	SEP #$20
	LDA.b #$81
	STA.l $002121
	REP #$20
	LDY.w #15
-	LDA.l !GhostPal,x
	SEP #$20
	STA.l $002122
	XBA
	STA.l $002122
	REP #$20
	INX
	INX
	DEY
	BNE -
	PLP
	PLY
	PLX
	RTS

DixieGlide:
	PHX
	LDA.l $7E0028
	SEC
	SBC.w #$0010
	STA.l !GlideOn              ; stale stamp = not gliding
	LDA.l !DFlag
	CMP.w #!Magic
	BNE .out
	LDA.l $7E056F               ; current lead Kong: 2 = Diddy slot (Dixie)
	CMP.w #$0002
	BNE .out
	LDX.b !CurIndex
	LDA.l $7E1029,x             ; state: 1 = jumping, or 0 with no ground (walked off a ledge)
	JSR IsAir
	BNE .out
	LDA.l $7E0EF1,x             ; Y speed (up is positive)
	BPL .out                    ; still rising
	LDA.l $7E050E               ; held buttons
	AND.w #$8000                ; B
	BEQ .out
	LDA.l $7E0EF1,x
	CMP.w #!GlideFall
	BCS +
	LDA.w #!GlideFall
	STA.l $7E0EF1,x
+	LDA.l !GlideCnt
	INC
	STA.l !GlideCnt
	LSR
	LSR                         ; new spin frame every 4 game frames
-	CMP.w #12
	BCC +
	SEC
	SBC.w #12
	BRA -
+	ASL
	ASL
	PHX
	TAX
	LDA.l !GlideTbl,x
	STA.l !GlideLo
	LDA.l !GlideTbl+2,x
	STA.l !GlideHi
	PLX
	TXA
	STA.l !GlideSlot
	LDA.w #$0000
	STA.l !DisplayedPose,x      ; force the graphics to re-upload every frame
	LDA.l $7E0028
	STA.l !GlideOn              ; stamp with the current frame
.out
	PLX
	LDA.w #$0002
	STA.b $84
	RTL

; Carried-barrel adjustment for the new Kongs (computed in the X hook, reused by the Y hook):
;   Kiddy (DK slot): hands at chest  -> forward +d, down d   (d ramps 0..16 during the lift)
;   Dixie (Diddy slot): hair overhead -> back e,   up 2e     (e ramps 0..11)
!BarDX = $7E04EA
!BarDY = $7E04EC
BarrelDelta:
	LDA.w #$0000
	STA.l !BarDX
	STA.l !BarDY
	LDA.w $145D,x               ; barrel's current height above the holder
	BMI .done
	PHA
	LDA.w $0D45,y               ; holder sprite ID
	CMP.w #$0001
	BEQ .kiddy
	CMP.w #$0002
	BEQ .dixie
	PLA
	BRA .done
.candy
	PLA
	CMP.w #$000B
	BCC +
	LDA.w #$000B
+	STA.l !BarDY                ; up to 11 px higher: she is taller than Diddy
	BRA .done
.kiddy
	LDA.l !KFlag
	CMP.w #!Magic
	BEQ +
	PLA
	BRA .done
+	PLA
	SEC
	SBC.w #$0010
	BMI .done
	CMP.w #$0010
	BCC +
	LDA.w #$0010
+	STA.l !BarDX
	EOR.w #$FFFF
	INC
	STA.l !BarDY
	BRA .done
.dixie
	LDA.l !DFlag
	CMP.w #!Magic2
	BEQ .candy
	CMP.w #!Magic
	BEQ +
	PLA
	BRA .done
+	PLA
	CMP.w #$000B
	BCC +
	LDA.w #$000B
+	PHA
	ASL
	STA.l !BarDY
	PLA
	EOR.w #$FFFF
	INC
	STA.l !BarDX
.done
	RTS

BarrelXR:                       ; facing right: X = holder X + offset + dx
	ADC.w $13E9,x
	PHA
	JSR BarrelDelta
	PLA
	CLC
	ADC.l !BarDX
	STA.w $0B19,x
	RTL

BarrelXL:                       ; facing left: X = holder X - offset - dx
	SBC.w $13E9,x
	PHA
	JSR BarrelDelta
	PLA
	SEC
	SBC.l !BarDX
	STA.w $0B19,x
	RTL

BarrelY:                        ; Y (up is positive) = holder Y + offset + dy
	ADC.w $145D,x
	CLC
	ADC.l !BarDY
	STA.w $0BC1,x
	RTL

KongMain:
	JSR HudLevelFrame
	LDA.b $84                   ; 0 = DK slot (Kiddy), 2 = Diddy slot
	BNE +
	JSR KiddyPound
+	LDX.b $84
	LDA.w $16FD,x
	RTL

KiddyPound:
	PHX
	LDA.l $7E0028
	SEC
	SBC.w #$0010
	STA.l !PoundStamp           ; no pose override unless set below
	LDA.l $7E0028               ; a pound can't survive the Kong vanishing (pit, level change)
	SEC
	SBC.l !PoundLast
	CMP.w #3
	BCC +
	LDA.w #$0000
	STA.l !PoundOn
+	LDA.l $7E0028
	STA.l !PoundLast
	LDA.l !KFlag
	CMP.w #!Magic
	BNE .cancel
	LDA.l $7E056F               ; Kiddy (DK slot) must be in the lead
	CMP.w #$0001
	BNE .cancel
	LDX.b !CurIndex
	LDA.l !PoundSit
	BEQ +
	JSR PoundSitHold
+	LDA.l !PoundOn
	BNE .active
	LDA.l $7E1029,x             ; start: in the air and Down pressed
	JSR IsAir
	BNE .out
	LDA.l $7E0510
	AND.w #$0400
	BEQ .out
	LDA.w #$0001
	STA.l !PoundOn
	LDA.w #$0000
	STA.l !PoundCnt
	LDA.l $7E0BC1,x
	STA.l !PoundY
.active
	LDA.l $7E1029,x
	JSR IsAir
	BEQ .air
	LDA.w #$0000                ; touched down (or got interrupted)
	STA.l !PoundOn
	STA.l !DisplayedPose,x      ; re-upload the real landing pose cleanly
	LDA.l $7E1029,x
	BEQ .land
	CMP.w #$0022                ; landed straight into a duck (Down still held)
	BNE .out
.land
	JSR PoundImpact
	LDA.w #$0001
	STA.l !PoundSit             ; keep sitting while Down stays held
	LDX.b !CurIndex
	JSR PoundSitHold            ; and show it from the very first ground frame
	BRA .out
.air
	JSR PoundAir
	BRA .out
.cancel
	LDA.w #$0000
	STA.l !PoundOn
	STA.l !PoundSit
.out
	PLX
	RTS

; Landing: thud, then hit everything in the box below Kiddy like Rambi's charge does
; (breakable floors/walls shatter, enemies are knocked out).
PoundImpact:
	LDA.w #$0015                ; heavy landing thud
	JSL $BFFB27
	LDX.w #$0032                ; make buried item caches hittable this frame,
-	LDA.w $0D45,x               ; exactly as a 160 px fall or DK's hand slap does
	CMP.w #$002C
	BNE +
	LDA.w $11A1,x
	ORA.w #$0001
	STA.w $11A1,x
+	DEX
	DEX
	BPL -
	LDX.b !CurIndex
	STX.b $B6
	LDY.w #PoundBox
	JSL $BBA4E5                 ; build the attack box from PoundBox
	LDA.w #$0023                ; Rambi/Enguarde attack classes + item caches
	JSL $BBA58D
	LDA.w #$0006                ; up to six things per pound
	STA.l !PoundCnt
.hit
	BCC .done
	LDY.b $88
	LDA.w #$0001
	STA.w $1595,y               ; "you've been hit"
	LDA.b !CurIndex
	STA.w $15C9,y
	LDA.w #$0000
	STA.w $0E89,y
	STA.w $0F25,y
	LDA.l !PoundCnt
	DEC
	STA.l !PoundCnt
	BEQ .done
	JSL $BBA594                 ; continue the scan from the last hit
	BRA .hit
.done
	LDA.w #$0000
	STA.l !PoundCnt
	RTS

PoundAir:
	LDA.w #$0000
	STA.l $7E0E89,x             ; no sideways drift during the move
	STA.l $7E0F25,x
	LDA.l !PoundCnt
	INC
	STA.l !PoundCnt
	CMP.w #!PoundHang
	BCS .drop
	LDA.l !PoundY               ; 1) hang in the air and flip
	STA.l $7E0BC1,x
	LDA.w #$0000
	STA.l $7E0EF1,x
	LDA.l !PoundCnt
	LSR                         ; flip frame = count / 2  (0..9)
	BRA .pose
.drop
	LDA.l $7E0BC1,x             ; 2) butt-first drop; counts as a 160 px fall
	CLC
	ADC.w #$00A0
	CMP.l $7E1B21
	BMI +
	STA.l $7E1B21
+	LDA.w #!PoundFall
	STA.l $7E0EF1,x
	LDA.w #!PoundSlam
.pose
	ASL
	ASL
	PHX
	TAX
	LDA.l !PoundTbl,x
	STA.l !PoundLo
	LDA.l !PoundTbl+2,x
	STA.l !PoundHi
	PLX
	TXA
	STA.l !PoundSlot
	LDA.w #$0000
	STA.l !DisplayedPose,x
	LDA.l $7E0028
	STA.l !PoundStamp
	RTS

!IconFrames = $7C0000           ; 8 x 0x400: original icon frames + faces at tiles $4C/$4E (+$5C-$5F)
!FacePal    = $403400           ; 13 colours for sprite palette 2, colours 3..15

IconSrc:                        ; A = source (low), X = bank, Y = size, as CODE_B999AD expects
	LDA.b $28
	LSR
	LSR
	LSR
	AND.w #$000F
	BIT.w #$0008
	BEQ +
	EOR.w #$000F
+	XBA
	ASL
	ASL                         ; frame * $400
	CLC
	ADC.w #!IconFrames&$FFFF
	LDX.w #!IconFrames>>16
	LDY.w #$0400
	RTL

IconAttr:                       ; A = original attribute, X = level index
	PHA
	LDA.l $7EFAFC,x
	AND.w #$00FF
	CMP.w #$0005
	BEQ .kiddy
	CMP.w #$0006
	BEQ .dixie
	CMP.w #$0007
	BEQ .cranky
	CMP.w #$0008
	BEQ .candy
	PLA
	BRA .store
.cranky
	PLA
	LDA.w #$246C                ; tile $6C, palette 2
	BRA .store
.candy
	PLA
	LDA.w #$246E
	BRA .store
.kiddy
	PLA
	LDA.w #$244C                ; tile $4C, palette 2
	BRA .store
.dixie
	PLA
	LDA.w #$244E
.store
	STA.w $0C69,y
	LDA.w #$0002
	RTL

WhoBeat:                        ; replaces TYA : LSR : ORA $4C  (Y = lead Kong's slot)
	TYA
	LSR
	PHA
	CMP.w #$0001
	BEQ .big
	CMP.w #$0002
	BNE .plain
	LDA.l !DFlag
	BRA .chk
.big
	LDA.l !KFlag
.chk
	CMP.w #!Magic2
	BEQ .cc
	CMP.w #!Magic
	BNE .plain
	PLA
	CLC
	ADC.w #$0004                ; 1 -> 5 (Kiddy), 2 -> 6 (Dixie)
	ORA.b $4C
	RTL
.cc
	PLA
	CLC
	ADC.w #$0006                ; 1 -> 7 (Cranky), 2 -> 8 (Candy)
	ORA.b $4C
	RTL
.plain
	PLA
	ORA.b $4C
	RTL

FacePalette:                    ; called after the map's sprite palette block is uploaded
	PHX
	PHP
	SEP #$20
	LDA.b #$A3                  ; sprite palette 2, colour 3
	STA.l $002121
	REP #$20
	LDX.w #$0000
-	LDA.l !FacePal,x
	SEP #$20
	STA.l $002122
	XBA
	STA.l $002122
	REP #$20
	INX
	INX
	CPX.w #26
	BCC -
	PLP
	PLX
	RTS

; After the slam: hold the seated pose while Down is held and Kiddy isn't crawling.
PoundSitHold:
	LDA.l $7E050E
	AND.w #$0400
	BEQ .stop
	LDA.l $7E1029,x
	BEQ +
	CMP.w #$0022
	BNE .stop
+	LDA.l $7E0E89,x             ; crawling? let the normal crawl play
	BNE .stop
	LDA.w #!PoundSlam
	ASL
	ASL
	PHX
	TAX
	LDA.l !PoundTbl,x
	STA.l !PoundLo
	LDA.l !PoundTbl+2,x
	STA.l !PoundHi
	PLX
	TXA
	STA.l !PoundSlot
	LDA.w #$0000
	STA.l !DisplayedPose,x
	LDA.l $7E0028
	STA.l !PoundStamp
	RTS
.stop
	LDA.w #$0000
	STA.l !PoundSit
	STA.l !DisplayedPose,x
	RTS

IsAir:                          ; A = state, X = slot. Z set if airborne:
	CMP.w #$0001                ;   jumping (1) ...
	BEQ .yes
	CMP.w #$0000                ;   ... or walking (0) with the on-ground bit clear
	BNE .no
	LDA.l $7E12A5,x
	AND.w #$0001
	BEQ .yes
.no
	LDA.w #$0001                ; Z clear
	RTS
.yes
	LDA.w #$0000                ; Z set
	RTS

AnyFlag:                        ; Z clear if Kiddy or Dixie is selected
	LDA.l !KFlag
	CMP.w #!Magic
	BEQ .yes
	LDA.l !DFlag
	CMP.w #!Magic
	BEQ .yes
	LDA.w #$0000
	RTS
.yes
	LDA.w #$0001
	RTS

FlagFor:                        ; A = 0 Kiddy, 1 Dixie, 2 Kiddy or Dixie, 3 Cranky, 4 Candy. Z clear if selected.
	CMP.w #$0002
	BEQ AnyFlag
	CMP.w #$0003
	BEQ .c
	CMP.w #$0004
	BEQ .y
	CMP.w #$0001
	BEQ .d
	LDA.l !KFlag
	BRA .chk
.d	LDA.l !DFlag
.chk
	CMP.w #!Magic
	BEQ .yes
.no	LDA.w #$0000
	RTS
.yes
	LDA.w #$0001
	RTS
.c	LDA.l !KFlag
	BRA .chk2
.y	LDA.l !DFlag
.chk2
	CMP.w #!Magic2
	BEQ .yes
	BRA .no

PoseSide:                       ; A = pose offset. Returns 0 for DK-side poses, 1 for Diddy-side.
	CMP.w #$0950                ; DK frames (incl. map DK) sit below $0950
	BCC .big
	CMP.w #$12AC                ; island DK
	BCC .small
	CMP.w #$12D0
	BCC .big
.small
	LDA.w #$0001
	RTS
.big
	LDA.w #$0000
	RTS

NextKong:                       ; 0 -> !Magic -> !Magic2 -> 0
	CMP.w #!Magic
	BEQ .two
	CMP.w #!Magic2
	BEQ .zero
	LDA.w #!Magic
	RTS
.two
	LDA.w #!Magic2
	RTS
.zero
	LDA.w #$0000
	RTS

KongOf:                         ; A = 0 big side, 1 small side -> A = that side's flag
	CMP.w #$0001
	BEQ +
	LDA.l !KFlag
	RTS
+	LDA.l !DFlag
	RTS

CCMapPalette:                   ; sprite palette 4 = Cranky/Candy map colours, or the original (blanking only)
	PHX
	PHY
	PHP
	REP #$30
	SEP #$20
	LDA.b #$C1
	STA.l $002121
	REP #$20
	LDA.l !KFlag
	CMP.w #!Magic2
	BEQ .cc
	LDA.l !DFlag
	CMP.w #!Magic2
	BEQ .cc
	LDX.w #$0000
-	LDA.l !MapPal4,x
	SEP #$20
	STA.l $002122
	XBA
	STA.l $002122
	REP #$20
	INX
	INX
	CPX.w #30
	BCC -
	BRA .out
.cc
	LDX.w #$0000
-	LDA.l !MapPalCC,x
	SEP #$20
	STA.l $002122
	XBA
	STA.l $002122
	REP #$20
	INX
	INX
	CPX.w #30
	BCC -
.out
	PLP
	PLY
	PLX
	RTS

IconDMA:                        ; runs in NMI right after the icon frame is sent to VRAM $0400
	JSL $B999AD
	REP #$30
	LDA.w #$06C0
	STA.l $002116
	LDA.w #!CCFaces&$FFFF
	LDX.w #!CCFaces>>16
	LDY.w #$0080
	JSL $B999AD
	REP #$30
	LDA.w #$07C0
	STA.l $002116
	LDA.w #(!CCFaces+$80)&$FFFF
	LDX.w #!CCFaces>>16
	LDY.w #$0080
	JSL $B999AD
	REP #$30
	LDA.w #$0E00                ; world-map stats HUD tiles at $E0-$EC
	STA.l $002116
	LDA.w #!HudTiles&$FFFF
	LDX.w #!HudTiles>>16
	LDY.w #13*32
	JSL $B999AD
	REP #$30
	RTL
